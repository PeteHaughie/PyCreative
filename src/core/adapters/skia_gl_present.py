"""Presenter adapter: manage a GL texture+FBO and a Skia Surface bound to it.

This adapter attempts to create a GPU-backed Skia surface (GrDirectContext +
backend render target) when an OpenGL context is available. If the GPU path
is not available it falls back to a CPU raster Skia Surface so callers still
receive a usable surface for headless rendering and testing.
"""
# mypy: ignore-errors
from __future__ import annotations

import logging
from typing import Any, Optional, Sequence


class SkiaGLPresenter:
    def __init__(self, width: int, height: int, force_present_mode: Optional[str] = None, force_gles: bool = False, window: Any | None = None):
        self.width = int(width)
        self.height = int(height)
        # Preserve the logical size the presenter was created for. The
        # presenter may resize its backing (device) texture/FBO to the
        # drawable/backing size during render; keep the original logical
        # size so we can compute the correct logical->backing scale for
        # HiDPI displays when replaying recorded commands.
        self._logical_size = (int(width), int(height))
        self.tex_id: Optional[int] = None
        self.fbo_id: Optional[int] = None
        self.gr_context = None
        self.surface = None
        # track the size the current Skia surface was created for
        self._surface_size: Optional[tuple[int, int]] = None
        # GL program / VBO for textured-quad fallback (GLSL 1.20 variant for macOS)
        self._fs_prog = None
        self._fs_prog_attrib_pos = None
        self._fs_prog_attrib_uv = None
        self._fs_prog_u_tex = None
        self._fs_prog_u_flip = None
        self._fs_vbo = None
        self._fs_vao = None
        # last present mode used: one of ('blit', 'vbo', 'immediate', None)
        self._last_present_mode = None
        # Optional override to force which present mode to use: 'vbo', 'blit', 'immediate' or None
        self.force_present_mode = force_present_mode
        # Optional window reference (passed by engine) so presenters can
        # query the underlying framebuffer size / pixel ratio when
        # allocating GL resources on HiDPI displays.
        self._window = window
        # If a window is provided, try to recover the logical (CSS) size
        # the engine expects. Engines may pass a backing/device-pixel
        # size when creating the presenter (to help allocate textures at
        # the correct size). If so, prefer deriving the logical size from
        # the window's pixel ratio so later replay scaling computes the
        # correct logical->backing scale (fixes HiDPI/Retina half-size
        # rendering when the presenter was constructed with backing dims).
        try:
            if self._window is not None:
                pr = getattr(self._window, 'get_pixel_ratio', None)
                if pr is not None:
                    try:
                        ratio = float(self._window.get_pixel_ratio())
                        if ratio and ratio != 1.0:
                            # Derive logical size from the provided width/height
                            # which may be a backing size. Use round to be safe
                            # against integer division rounding differences.
                            try:
                                self._logical_size = (int(round(self.width / ratio)), int(round(self.height / ratio)))
                            except Exception:
                                # Fall back to the original values on error
                                self._logical_size = (int(width), int(height))
                    except Exception:
                        # If get_pixel_ratio exists but fails, keep provided logical size
                        self._logical_size = (int(width), int(height))
                else:
                    # No pixel-ratio helper; keep the size as provided
                    self._logical_size = (int(width), int(height))
        except Exception:
            # Defensive fallback to original behaviour
            self._logical_size = (int(width), int(height))
        # Debug: report what logical size we ended up with and the window's
        # pixel ratio (if available). This helps triage cases where the
        # presenter was constructed with backing dimensions and the
        # logical size derivation may have failed or been skipped.
        try:
            try:
                pr = None
                if getattr(self, '_window', None) is not None:
                    pr_fn = getattr(self._window, 'get_pixel_ratio', None)
                    if pr_fn is not None:
                        try:
                            pr = float(self._window.get_pixel_ratio())
                        except Exception:
                            pr = None
                logging.getLogger(__name__).debug('SkiaGLPresenter.__init__: window=%r pixel_ratio=%r derived_logical=%r ctor_w=%r ctor_h=%r', getattr(self, '_window', None), pr, getattr(self, '_logical_size', None), width, height)
            except Exception:
                pass
        except Exception:
            pass
        # diagnostics printed once on first present
        self._present_diag_done = False
        # optional testing flag: force using GLES shader variant (if available)
        self.force_gles = bool(force_gles)

    def _sniff_gles3_support(self) -> bool:
        """Return True if the current GL context appears to support GLES3-style shading.

        This is a heuristic: we test whether the GL shading language version
        string contains 'GLES' or whether GL version indicates an ES context.
        """
        try:
            from pyglet import gl
            s = None
            try:
                raw = gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
                if raw:
                    s = raw.decode('utf-8', 'ignore')
            except Exception:
                s = None
            if s and 'ES' in s:
                return True
            # Also check GL_VERSION for 'OpenGL ES' substring
            try:
                rawv = gl.glGetString(gl.GL_VERSION)
                if rawv:
                    sv = rawv.decode('utf-8', 'ignore')
                    if 'OpenGL ES' in sv or 'GLES' in sv:
                        return True
            except Exception:
                pass
        except Exception:
            pass
        return False

    # Test helper: return the ordering of shader variants that would be
    # attempted. Accepts optional overrides to avoid requiring a GL context
    # during tests.
    def _variant_ordering(self, force_gles_override: Optional[bool] = None, sniff_override: Optional[bool] = None):
        """Return a list of variant tags in preferred order.

        Used by unit tests to assert the order without invoking GL.
        """
        try:
            prefer_es = bool(self.force_gles)
            if force_gles_override is not None:
                prefer_es = bool(force_gles_override)
            elif sniff_override is not None:
                # sniff_override takes precedence over actual sniffing
                prefer_es = bool(sniff_override)
            else:
                try:
                    prefer_es = bool(self.force_gles) or self._sniff_gles3_support()
                except Exception:
                    prefer_es = bool(self.force_gles)
        except Exception:
            prefer_es = bool(self.force_gles)
        if prefer_es:
            return ['es300', '150', '120']
        return ['150', 'es300', '120']

    def ensure_resources(self):
        """Create GL texture and FBO if they don't already exist.

        This method has been factored into a helper module to keep the
        presenter shim small. Delegate to the resources helper.
        """
        from ._skia_gl_present_resources import ensure_resources as _ensure_resources
        return _ensure_resources(self)

    def create_skia_surface(self) -> Any:
        """Create a GPU-backed Skia surface bound to our FBO.

        This is GPU-only: if the GPU-backed Skia surface cannot be created
        the method returns None. Callers should treat failure as a fatal
        condition for GPU rendering and may implement their own fallbacks.
        """
        # Delegate creation to the resources helper which implements the
        # original method body. Keeping this method small preserves the
        # public API while moving the monolithic implementation out.
        from ._skia_gl_present_resources import create_skia_surface as _create_skia_surface
        return _create_skia_surface(self)

    def render_commands(self, commands: Sequence[dict], replay_fn) -> Any:
        """Render a recorded command list into the GPU-backed Skia surface.

        This presenter is GPU-only: `create_skia_surface()` must return a
        valid GPU surface. If surface creation fails this function raises.
        """
        # Delegate the full rendering/present/command-preprocessing
        # implementation to the extract located in
        # `src/core/adapters/_skia_gl_present_render.py`.
        from ._skia_gl_present_render import render_commands as _render_commands
        return _render_commands(self, commands, replay_fn)

    def replay_fn(self, commands, canvas):
        # Delegate to the centralized replayer implementation in the
        # extracted render module. This keeps the presenter file thin and
        # ensures a single canonical implementation is used.
        from ._skia_gl_present_render import replay_fn as _replay_fn
        return _replay_fn(self, commands, canvas)

    def teardown(self):
        # Delegate teardown to the render helper which centralises
        # GL + Skia resource cleanup logic.
        from ._skia_gl_present_render import teardown as _teardown
        return _teardown(self)

    def resize(self, width: int, height: int):
        """Resize the presenter's backing texture/FBO and drop any Skia surface.

        This tears down existing GL and Skia resources; caller should then
        call ensure_resources()/create_skia_surface() via render_commands.
        """
        # Delegate resizing to the render helper which handles resource
        # recreation and HiDPI bookkeeping in a single place.
        from ._skia_gl_present_render import resize as _resize
        return _resize(self, width, height)

    # --- textured-quad (VBO + GLSL 1.20) helpers ---
    def _compile_shader(self, source: str, shader_type):
        from ._skia_gl_present_vbo import _compile_shader as _v_compile
        return _v_compile(self, source, shader_type)

    def _link_program(self, vert, frag, bind_attribs=None):
        from ._skia_gl_present_vbo import _link_program as _v_link
        return _v_link(self, vert, frag, bind_attribs=bind_attribs)

    def _ensure_textured_quad_resources(self):
        """Create GLSL 1.20 program and a static VBO for a fullscreen quad."""
        from ._skia_gl_present_vbo import _ensure_textured_quad_resources as _ensure
        return _ensure(self)

    def _draw_textured_quad_vbo(self, tex_id: int, flip_y: bool = True):
        from ._skia_gl_present_vbo import _draw_textured_quad_vbo as _v_draw
        return _v_draw(self, tex_id, flip_y=flip_y)

