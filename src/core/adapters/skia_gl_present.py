"""Presenter adapter: manage a GL texture+FBO and a Skia Surface bound to it.

This adapter attempts to create a GPU-backed Skia surface (GrDirectContext +
backend render target) when an OpenGL context is available. If the GPU path
is not available it falls back to a CPU raster Skia Surface so callers still
receive a usable surface for headless rendering and testing.
"""
# mypy: ignore-errors
from __future__ import annotations

import ctypes
import logging
from typing import Any, Optional, Sequence
import os
import json
import time


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
        """Create GL texture and FBO if they don't already exist."""
        # Lazy import to avoid top-level pyglet dependency
        from pyglet import gl

        if self.tex_id is None:
            tex = gl.GLuint()
            gl.glGenTextures(1, ctypes.byref(tex))
            self.tex_id = int(tex.value)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex_id)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            # Prefer allocating the texture at the drawable/backing size
            # (device pixels) when available. First prefer an explicit
            # window-provided framebuffer size (engine passes the window
            # into the presenter where supported). Next try the pixel
            # ratio helpers. Finally fall back to querying the GL
            # viewport. As a last resort use the presenter's logical
            # width/height.
            bw = bh = None
            try:
                if getattr(self, '_window', None) is not None:
                    try:
                        # Some window implementations expose get_framebuffer_size()
                        fb = getattr(self._window, 'get_framebuffer_size', None)
                        if fb is not None:
                            fw, fh = self._window.get_framebuffer_size()
                            if fw and fh:
                                bw, bh = int(fw), int(fh)
                        else:
                            # Fall back to get_pixel_ratio if framebuffer API
                            pr = getattr(self._window, 'get_pixel_ratio', None)
                            if pr is not None:
                                ratio = float(self._window.get_pixel_ratio())
                                if ratio and ratio != 1.0:
                                    bw = int(self.width * ratio)
                                    bh = int(self.height * ratio)
                    except Exception:
                        bw = bh = None
            except Exception:
                bw = bh = None

            if bw is None or bh is None:
                try:
                    vp = (gl.GLint * 4)()
                    gl.glGetIntegerv(gl.GL_VIEWPORT, vp)
                    bw = int(vp[2])
                    bh = int(vp[3])
                    if bw <= 0 or bh <= 0:
                        raise Exception('invalid viewport')
                except Exception:
                    bw = int(self.width)
                    bh = int(self.height)

            # Use RGBA8 where available; fallback to RGBA
            try:
                internal = gl.GL_RGBA8
            except Exception:
                internal = gl.GL_RGBA
            # record backing size for later use by Skia surface creation
            try:
                self._backing_size = (int(bw), int(bh))
            except Exception:
                pass
            # Debug: record the exact size used to allocate the GL texture
            try:
                try:
                    logging.getLogger(__name__).debug('ensure_resources: allocating GL texture tex_id=%s size=%s', self.tex_id, (int(bw), int(bh)))
                except Exception:
                    pass
                try:
                    with open('/tmp/pycreative_present_allocations.log', 'a') as _af:
                        _af.write(f'{time.time():.6f} ensure_resources: tex_id={self.tex_id} alloc_w={int(bw)} alloc_h={int(bh)}\n')
                except Exception:
                    pass
            except Exception:
                pass
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, internal, bw, bh, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
            # After GL resources are available, attempt to compile any
            # registered PCShader objects so they can be used at runtime.
            try:
                try:
                    import pycreative.graphics as _gfx
                    shaders = getattr(_gfx, '_REGISTERED_SHADERS', None)
                    if shaders is not None:
                        for s in list(shaders):
                            try:
                                # only attempt compile for shaders with fragment source
                                if not getattr(s, 'frag_source', None):
                                    continue

                                # We'll attempt compilation using the presenter's preferred
                                # GLSL variant ordering. For each variant we prepend a
                                # suitable #version directive (and ES precision when
                                # needed) and try compiling both vertex and fragment
                                # sources. If the shader originally used the default
                                # vert_source we substitute a variant-appropriate
                                # passthrough vertex shader so compilation succeeds.
                                variants = self._variant_ordering()
                                compiled_prog = None
                                last_exc = None
                                for var in variants:
                                    # conservative sanitizer to adapt shader text per-variant
                                    def _sanitize_source(src: str | None, stage: str, variant_tag: str) -> str:
                                        if src is None:
                                            return ''
                                        s = src
                                        try:
                                            s = s.lstrip('\ufeff\n\r \t')
                                        except Exception:
                                            s = s.lstrip()
                                        try:
                                            idx = s.find('#version')
                                            if idx > 0:
                                                s = s[idx:]
                                        except Exception:
                                            pass
                                        try:
                                            if variant_tag in ('150', 'es300'):
                                                s = s.replace('texture2D(', 'texture(')
                                                if stage == 'frag' and 'gl_FragColor' in s:
                                                    s = s.replace('gl_FragColor', 'fragColor')
                                                    if '#version' in s:
                                                        parts = s.split('\n', 1)
                                                        first = parts[0]
                                                        rest = parts[1] if len(parts) > 1 else ''
                                                        if 'out vec4 fragColor' not in s:
                                                            rest = 'out vec4 fragColor;\n' + rest
                                                        s = first + '\n' + rest
                                                if stage == 'vert':
                                                    s = s.replace('attribute ', 'in ')
                                                    s = s.replace('varying ', 'out ')
                                                if stage == 'frag':
                                                    s = s.replace('varying ', 'in ')
                                        except Exception:
                                            pass
                                        try:
                                            if s.count('#version') > 1:
                                                first = s.find('#version')
                                                rest = s[first:]
                                                lines = rest.split('\n')
                                                first_line = lines[0]
                                                others = [ln for ln in lines[1:] if '#version' not in ln]
                                                s = first_line + '\n' + '\n'.join(others)
                                        except Exception:
                                            pass
                                        return s

                                    try:
                                        v_prefix = ''
                                        frag_prefix = ''
                                        vert_src = getattr(s, 'vert_source', None)
                                        # Map variant tags to #version lines and defaults
                                        if var == '150':
                                            frag_prefix = '#version 150\n'
                                            vert_prefix = '#version 150\n'
                                            # modern in/out style
                                            default_vert = ('#version 150\n'
                                                            'in vec2 position;\n'
                                                            'in vec2 texcoord0;\n'
                                                            'out vec2 v_texcoord;\n'
                                                            'void main() { v_texcoord = texcoord0; gl_Position = vec4(position, 0.0, 1.0); }')
                                        elif var == 'es300':
                                            frag_prefix = '#version 300 es\nprecision mediump float;\n'
                                            vert_prefix = '#version 300 es\n'
                                            default_vert = ('#version 300 es\n'
                                                            'in vec2 position;\n'
                                                            'in vec2 texcoord0;\n'
                                                            'out vec2 v_texcoord;\n'
                                                            'void main() { v_texcoord = texcoord0; gl_Position = vec4(position, 0.0, 1.0); }')
                                        else:
                                            # fallback to legacy 120
                                            frag_prefix = '#version 120\n'
                                            vert_prefix = '#version 120\n'
                                            default_vert = ('#version 120\n'
                                                            'attribute vec2 position;\n'
                                                            'attribute vec2 texcoord0;\n'
                                                            'varying vec2 v_texcoord;\n'
                                                            'void main() { v_texcoord = texcoord0; gl_Position = vec4(position, 0.0, 1.0); }')

                                        # Choose vertex source: if the shader's vert_source is
                                        # exactly the library default (no version) or is None,
                                        # use our variant-appropriate default. Otherwise try
                                        # to compile the provided source with the prefix.
                                        provided_vert = getattr(s, 'vert_source', None)
                                        use_vert = None
                                        try:
                                            # Heuristic: if provided_vert is None or seems to
                                            # be the default passthrough (matches our earlier
                                            # default pattern without a #version), substitute.
                                            if not provided_vert:
                                                use_vert = default_vert
                                            else:
                                                # Sanitize provided vertex source for variant
                                                try:
                                                    provided_vert = _sanitize_source(provided_vert, 'vert', var)
                                                except Exception:
                                                    pass
                                                # If provided_vert already contains a #version,
                                                # trust it; otherwise prepend the variant prefix.
                                                if '#version' in provided_vert:
                                                    use_vert = provided_vert
                                                else:
                                                    use_vert = vert_prefix + provided_vert
                                        except Exception:
                                            use_vert = default_vert

                                        # Prepare fragment source with appropriate prefix
                                        frag_src_try = s.frag_source or ''
                                        try:
                                            frag_src_try = _sanitize_source(frag_src_try, 'frag', var)
                                        except Exception:
                                            pass
                                        if '#version' not in frag_src_try:
                                            frag_src_try = frag_prefix + frag_src_try.lstrip()

                                        # Now compile and link
                                        frag_sh = self._compile_shader(frag_src_try, gl.GL_FRAGMENT_SHADER)
                                        vert_sh = self._compile_shader(use_vert, gl.GL_VERTEX_SHADER)
                                        prog = self._link_program(vert_sh, frag_sh)
                                        compiled_prog = int(prog)
                                        # success -> attach and break
                                        try:
                                            s._program = compiled_prog
                                            try:
                                                s._compiled_variant = var
                                            except Exception:
                                                pass
                                            try:
                                                logging.getLogger(__name__).debug('Compiled PCShader using variant %s prog=%s', var, compiled_prog)
                                            except Exception:
                                                pass
                                        except Exception:
                                            pass
                                        break
                                    except Exception as e:
                                        last_exc = e
                                        # try next variant
                                        continue

                                if compiled_prog is None:
                                    try:
                                        logging.getLogger(__name__).exception('Failed to compile/link PCShader')
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                except Exception:
                    pass
            except Exception:
                pass
            # If a setup background color is known, initialize the texture
            # contents to that opaque color so alpha isn't left zero. This
            # protects against drivers or Skia surface creation paths that
            # leave the texture uninitialized with alpha=0.
            try:
                bg = getattr(self, '_setup_background_color', None)
                if bg is not None:
                    # Create a small buffer filled with (r,g,b,255) bytes
                    try:
                        r = int(bg[0]) & 0xFF
                        g = int(bg[1]) & 0xFF
                        b = int(bg[2]) & 0xFF
                        w = int(self.width)
                        h = int(self.height)
                        buf_len = w * h * 4
                        arr_type = (gl.GLubyte * buf_len)
                        buf = arr_type()
                        # Fill with RGBA tuples
                        idx = 0
                        for _ in range(w * h):
                            buf[idx] = r
                            buf[idx + 1] = g
                            buf[idx + 2] = b
                            buf[idx + 3] = 255
                            idx += 4
                        # Upload as full texture data — ensure unpack alignment = 1
                        try:
                            try:
                                gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
                            except Exception:
                                pass
                            try:
                                gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, w, h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, buf)
                            except Exception:
                                # Some platforms may require a pointer cast
                                try:
                                    gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, w, h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.byref(buf))
                                except Exception:
                                    pass
                        finally:
                            try:
                                gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 4)
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
            try:
                if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                    try:
                        logging.getLogger(__name__).debug('ensure_resources created tex_id=%s', self.tex_id)
                    except Exception:
                        pass
            except Exception:
                pass

        if self.fbo_id is None:
            fbo = gl.GLuint()
            gl.glGenFramebuffers(1, ctypes.byref(fbo))
            self.fbo_id = int(fbo.value)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, int(self.fbo_id))
            # Make sure the viewport matches the backing size when the
            # FBO is bound so GPU drawing (and Skia) has the correct extents.
            try:
                try:
                    bw, bh = getattr(self, '_backing_size')
                except Exception:
                    bw, bh = int(self.width), int(self.height)
                if bw and bh:
                    try:
                        gl.glViewport(0, 0, int(bw), int(bh))
                    except Exception:
                        pass
            except Exception:
                pass
            # attach texture
            try:
                gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, int(self.tex_id), 0)
            except Exception:
                # some drivers expose glFramebufferTexture2D on a different symbol
                try:
                    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, int(self.tex_id), 0)
                except Exception:
                    pass
            try:
                if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                    try:
                        logging.getLogger(__name__).debug('ensure_resources created fbo_id=%s', self.fbo_id)
                    except Exception:
                        pass
            except Exception:
                pass
            # check completeness
            try:
                status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
                if status != gl.GL_FRAMEBUFFER_COMPLETE:
                    # leave bound but note that it may be unusable
                    print('SkiaGLPresenter: FBO incomplete status=', status)
            except Exception:
                pass
            # unbind
            try:
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            except Exception:
                pass

    def create_skia_surface(self) -> Any:
        """Create a GPU-backed Skia surface bound to our FBO.

        This is GPU-only: if the GPU-backed Skia surface cannot be created
        the method returns None. Callers should treat failure as a fatal
        condition for GPU rendering and may implement their own fallbacks.
        """
        try:
            import skia
        except Exception:
            return None

        # Ensure GL objects exist (tex/fbo) so a GPU backend target can be built.
        try:
            self.ensure_resources()
        except Exception:
            pass

        try:
            try:
                if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                    try:
                        logging.getLogger(__name__).debug('create_skia_surface: entry fbo=%s tex=%s', self.fbo_id, self.tex_id)
                    except Exception:
                        pass
            except Exception:
                pass
            # Create GrDirectContext bound to current GL context
            # If we already have a surface and gr_context for the same size,
            # reuse it to preserve GPU-side pixels across frames rather
            # than recreating a new Skia surface each frame.
            # If we already have a surface and gr_context for the same
            # device-pixel backing size, reuse it. Compare against the
            # recorded backing size rather than the logical presenter
            # width/height to avoid reusing a surface created for the
            # wrong framebuffer scale (HiDPI displays).
            try:
                current_backing = getattr(self, '_backing_size')
            except Exception:
                current_backing = (int(self.width), int(self.height))
            if getattr(self, 'surface', None) is not None and getattr(self, 'gr_context', None) is not None and self._surface_size == (int(current_backing[0]), int(current_backing[1])):
                try:
                        if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                            try:
                                logging.getLogger(__name__).debug('create_skia_surface: reusing existing GPU surface')
                            except Exception:
                                pass
                        return self.surface
                except Exception:
                    return self.surface

            ctx = skia.GrDirectContext.MakeGL()
            if ctx is None:
                try:
                    if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                        try:
                            logging.getLogger(__name__).debug('create_skia_surface: GrDirectContext.MakeGL() returned None')
                        except Exception:
                            pass
                except Exception:
                    pass
                return None

            from pyglet import gl

            try:
                fb_fmt = int(gl.GL_RGBA8)
            except Exception:
                fb_fmt = int(gl.GL_RGBA)

            # Prefer to create the backend render target at the device pixel
            # backing size recorded when the GL texture was allocated.
            try:
                bw, bh = getattr(self, '_backing_size')
            except Exception:
                bw, bh = int(self.width), int(self.height)
            # Debug: record the size used to create the GrBackendRenderTarget
            try:
                try:
                    logging.getLogger(__name__).debug('create_skia_surface: creating backend RT fbo=%s tex=%s size=%s', self.fbo_id, self.tex_id, (int(bw), int(bh)))
                except Exception:
                    pass
                try:
                    with open('/tmp/pycreative_present_allocations.log', 'a') as _af:
                        _af.write(f'create_skia_surface: fbo={self.fbo_id} tex={self.tex_id} rt_w={int(bw)} rt_h={int(bh)}\n')
                except Exception:
                    pass
            except Exception:
                pass
            fb_info = skia.GrGLFramebufferInfo(int(self.fbo_id or 0), fb_fmt)
            backend_rt = skia.GrBackendRenderTarget(int(bw), int(bh), 0, 0, fb_info)
            surf = skia.Surface.MakeFromBackendRenderTarget(
                ctx,
                backend_rt,
                skia.kBottomLeft_GrSurfaceOrigin,
                skia.kRGBA_8888_ColorType,
                skia.ColorSpace.MakeSRGB(),
            )
            if surf is None:
                try:
                        if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                            try:
                                logging.getLogger(__name__).debug('create_skia_surface: MakeFromBackendRenderTarget returned None')
                            except Exception:
                                pass
                except Exception:
                    pass
                return None

            self.gr_context = ctx
            self.surface = surf
            try:
                # Record the actual device-pixel size the Skia surface was
                # created for. Use the recorded backing size when available
                # and fall back to the presenter's configured width/height.
                try:
                    bw, bh = getattr(self, '_backing_size', (int(self.width), int(self.height)))
                except Exception:
                    bw, bh = int(self.width), int(self.height)
                self._surface_size = (int(bw), int(bh))
                # Also update backing size to match the surface to keep
                # other code paths consistent.
                try:
                    self._backing_size = (int(bw), int(bh))
                except Exception:
                    pass
            except Exception:
                self._surface_size = None
            try:
                if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                    try:
                        logging.getLogger(__name__).debug('create_skia_surface: created GPU surface fbo=%s tex=%s size=%s %s', self.fbo_id, self.tex_id, self.width, self.height)
                    except Exception:
                        pass
            except Exception:
                pass
            return surf
        except Exception:
            return None

    def render_commands(self, commands: Sequence[dict], replay_fn) -> Any:
        """Render a recorded command list into the GPU-backed Skia surface.

        This presenter is GPU-only: `create_skia_surface()` must return a
        valid GPU surface. If surface creation fails this function raises.
        """
        try:
            if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                try:
                    logging.getLogger(__name__).debug('render_commands: entry commands=%s', len(commands))
                except Exception:
                    pass
        except Exception:
            pass

        # Ensure GL objects exist
        try:
            self.ensure_resources()
        except Exception:
            pass

        surf = self.create_skia_surface()
        if surf is None:
            raise RuntimeError('Failed to create a GPU Skia surface')

        # If we have a GPU-backed GrDirectContext + FBO, bind the FBO so Skia draws there.
        using_gpu = getattr(self, 'gr_context', None) is not None
        if using_gpu:
            from pyglet import gl
            try:
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, int(self.fbo_id or 0))
            except Exception:
                pass
            # Debug: log current GL viewport and bound FBO to diagnose HiDPI mapping
            try:
                vp = (gl.GLint * 4)()
                gl.glGetIntegerv(gl.GL_VIEWPORT, vp)
                try:
                    fb = (gl.GLint)()
                    gl.glGetIntegerv(gl.GL_FRAMEBUFFER_BINDING, fb)
                    logging.getLogger(__name__).debug('render_commands: GL viewport=%s bound_fbo=%s', (int(vp[2]), int(vp[3])), int(fb.value))
                except Exception:
                    logging.getLogger(__name__).debug('render_commands: GL viewport=%s', (int(vp[2]), int(vp[3])))
            except Exception:
                pass

        # Get canvas and replay commands
        try:
            canvas = surf.getCanvas()
        except Exception:
            # Older skia bindings / unexpected surface types
            canvas = None

        if canvas is None:
            try:
                if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                    try:
                        logging.getLogger(__name__).debug('render_commands: surface.getCanvas() returned None')
                    except Exception:
                        pass
            except Exception:
                pass
            raise RuntimeError('Skia surface does not provide a canvas')

        # Do not clear the canvas here. The replay function is responsible
        # for applying any background command. Leaving the FBO contents
        # intact when no background is provided implements the Processing
        # semantics where drawings persist across frames unless explicitly
        # cleared by `background()`.

        # Call the replay function provided by the engine to draw recorded ops
        try:
            if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                try:
                    logging.getLogger(__name__).debug('render_commands: calling replay_fn with %s commands', len(commands))
                except Exception:
                    pass
        except Exception:
            pass

        # The recorded commands are in logical (CSS) pixels. When replaying
        # into a GPU-backed Skia surface that is created at device/backing
        # pixels we must scale the Skia canvas so the replayer can draw in
        # logical coordinates and the output maps correctly onto the
        # backing texture (fixes HiDPI/Retina half-size rendering).
        try:
            bw, bh = None, None
            try:
                if getattr(self, '_surface_size', None):
                    bw, bh = self._surface_size
            except Exception:
                bw, bh = None, None
            if bw is None or bh is None:
                try:
                    if getattr(self, '_backing_size', None):
                        bw, bh = self._backing_size
                except Exception:
                    bw, bh = None, None

            # Use the preserved logical size (the size the presenter was
            # initially created with) when computing the replay scale.
            # Fall back to the presenter's current width/height if the
            # logical size is not available for any reason.
            try:
                lw, lh = getattr(self, '_logical_size', (None, None))
                lw = int(lw) if lw is not None else int(getattr(self, 'width', 0) or 0)
                lh = int(lh) if lh is not None else int(getattr(self, 'height', 0) or 0)
            except Exception:
                lw = int(getattr(self, 'width', 0) or 0)
                lh = int(getattr(self, 'height', 0) or 0)

            # Debug: log the resolved sizes used for potential scaling so we
            # can diagnose why the scale path may be skipped on some runs.
            try:
                logging.getLogger(__name__).debug('render_commands: resolved sizes bw=%r bh=%r lw=%r lh=%r', bw, bh, lw, lh)
            except Exception:
                pass
            try:
                # Write a small trace into repo-local tmp so we can inspect
                # sizes without relying on terminal output (avoids binary
                # flooding/truncation during analysis runs).
                _dbg_path = 'tmp/pycreative_present_resolved_sizes.log'
                try:
                    with open(_dbg_path, 'a') as _df:
                        _df.write(f"resolved sizes bw={bw} bh={bh} lw={lw} lh={lh}\n")
                except Exception:
                    pass
            except Exception:
                pass

            if bw and bh and lw and lh:
                try:
                    sx = float(bw) / float(lw)
                    sy = float(bh) / float(lh)
                    # debug log
                    try:
                        logging.getLogger(__name__).debug('render_commands: applying canvas scale sx=%r sy=%r (bw=%r bh=%r lw=%r lh=%r)', sx, sy, bw, bh, lw, lh)
                    except Exception:
                        pass

                    # Log canvas state before applying scale so we can compare
                    # to the canvas observed inside the replayer.
                    try:
                        try:
                            _bef = canvas.getTotalMatrix().asAffine()
                        except Exception:
                            # some skia-python versions differ
                            try:
                                _bef = canvas.getTotalMatrix().asM33()
                            except Exception:
                                _bef = None
                        logging.getLogger(__name__).debug('render_commands: canvas BEFORE scale id=%r matrix=%r', id(canvas), _bef)
                    except Exception:
                        pass
                    try:
                        _dbg_path = 'tmp/pycreative_present_canvas_before.log'
                        try:
                            with open(_dbg_path, 'a') as _df:
                                _df.write(f"BEFORE id={id(canvas)} matrix={_bef}\n")
                        except Exception:
                            pass
                    except Exception:
                        pass

                    # save/restore so we don't leak transforms
                    try:
                        canvas.save()
                    except Exception:
                        pass

                    # Try to scale; fall back to matrix concat if needed
                    try:
                        canvas.scale(sx, sy)
                    except Exception:
                        try:
                            import skia as _skia
                            m = _skia.Matrix()
                            m.setScale(sx, sy)
                            canvas.concat(m)
                        except Exception:
                            pass

                    # Log canvas state after applying scale so we can verify the
                    # transform took effect on the same canvas object.
                    try:
                        try:
                            _aft = canvas.getTotalMatrix().asAffine()
                        except Exception:
                            try:
                                _aft = canvas.getTotalMatrix().asM33()
                            except Exception:
                                _aft = None
                        logging.getLogger(__name__).debug('render_commands: canvas AFTER scale id=%r matrix=%r', id(canvas), _aft)
                    except Exception:
                        pass
                    try:
                        _dbg_path = 'tmp/pycreative_present_canvas_after.log'
                        try:
                            with open(_dbg_path, 'a') as _df:
                                _df.write(f"AFTER id={id(canvas)} matrix={_aft}\n")
                        except Exception:
                            pass
                    except Exception:
                        pass

                    # Optional forced full-coverage test draw (draws a semi-transparent
                    # red rectangle across the logical canvas so we can verify the
                    # Skia->FBO->present pipeline actually wrote to the full backing).
                    try:
                        if os.getenv('PYCREATIVE_DEBUG_FORCE_FULL_DRAW', '') == '1':
                            try:
                                import skia as _skia
                                _paint = _skia.Paint()
                                _paint.setStyle(_skia.Paint.kFill_Style)
                                # semi-transparent red
                                try:
                                    _paint.setColor(_skia.ColorSetARGB(192, 255, 0, 0))
                                except Exception:
                                    try:
                                        _paint.setColor(0xC0FF0000)
                                    except Exception:
                                        pass
                                # draw in logical coordinates (will be scaled)
                                try:
                                    _rect = _skia.Rect.MakeLTRB(0, 0, float(lw), float(lh))
                                    canvas.drawRect(_rect, _paint)
                                except Exception:
                                    try:
                                        canvas.drawRect(0, 0, float(lw), float(lh), _paint)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                    except Exception:
                        pass

                    try:
                        logging.getLogger(__name__).debug('render_commands: about to call replay_fn id=%r', id(canvas))
                    except Exception:
                        pass
                    try:
                        _dbg_path = 'tmp/pycreative_present_about_to_replay.log'
                        try:
                            with open(_dbg_path, 'a') as _df:
                                _df.write(f"ABOUT_TO_REPLAY id={id(canvas)}\n")
                        except Exception:
                            pass
                    except Exception:
                        pass

                    try:
                        replay_fn(commands, canvas)
                    finally:
                        try:
                            canvas.restore()
                        except Exception:
                            pass
                    # we've delegated and restored, skip the default call
                    goto_skip = True
                except Exception:
                    goto_skip = False
            else:
                goto_skip = False
        except Exception:
            goto_skip = False

        if not (locals().get('goto_skip', False)):
            replay_fn(commands, canvas)

        # Flush/submit
        try:
            surf.flush()
        except Exception:
            pass

        try:
            if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                try:
                    logging.getLogger(__name__).debug('render_commands: surf.flush() completed')
                except Exception:
                    pass
        except Exception:
            pass

        # Ensure GPU work is flushed/submitted so snapshot/readback sees rendered pixels
        try:
            if self.gr_context is not None:
                if hasattr(self.gr_context, 'flush'):
                    self.gr_context.flush()
                if hasattr(self.gr_context, 'submit'):
                    self.gr_context.submit()
        except Exception:
            pass

        # GL sync
        try:
            from pyglet import gl as _gl
            _gl.glFlush()
            _gl.glFinish()
        except Exception:
            pass

        # Small diagnostic: log whether any save_frame commands are present
        # and the total command count. Use the module logger rather than
        # writing to /tmp or printing to stdout so production runs stay quiet.
        try:
            try:
                sf_count = sum(1 for c in commands if c.get('op') == 'save_frame')
            except Exception:
                sf_count = 0
            try:
                logging.getLogger(__name__).debug('render_commands commands=%d save_frame_count=%d', len(commands), sf_count)
            except Exception:
                pass
        except Exception:
            pass

        # Process any recorded save_frame commands here so they are handled
        # regardless of which present path (blit/vbo/immediate) is used.
        try:
            # iterate over a copy to avoid concurrent mutation issues
            for idx, cmd in enumerate(list(commands)):
                try:
                    if cmd.get('op') != 'save_frame':
                        continue
                    args = cmd.get('args', {}) or {}
                    path = args.get('path') or args.get('p') or args.get('a')
                    if not path:
                        continue

                    # lightweight trace via logger (avoid noisy /tmp writes)
                    try:
                        logging.getLogger(__name__).debug('SAVE_FRAME idx=%d path=%s total_cmds=%d', idx, path, len(commands))
                    except Exception:
                        pass

                    # Extra debug: report presenter/skia surface sizes so we can
                    # diagnose mismatches between the Skia surface, presenter
                    # reported width/height, and the GL readback dimensions.
                    try:
                        logger = logging.getLogger(__name__)
                        surf_size = getattr(self, '_surface_size', None)
                        logger.debug('SAVE_FRAME sizes presenter.width=%s presenter.height=%s _surface_size=%s fbo=%s', getattr(self, 'width', None), getattr(self, 'height', None), surf_size, getattr(self, 'fbo_id', None))
                        # Also write a small debug record to /tmp so CLI runs can inspect
                        try:
                            with open('/tmp/pycreative_saveframe_debug.txt', 'a') as _df:
                                _df.write(f'SAVE_FRAME sizes presenter.width={getattr(self, "width", None)} presenter.height={getattr(self, "height", None)} _surface_size={surf_size} fbo={getattr(self, "fbo_id", None)}\n')
                        except Exception:
                            pass
                    except Exception:
                        pass

                    # Try Skia snapshot first
                    try:
                        img = None
                        try:
                            img = surf.makeImageSnapshot()
                        except Exception as e:
                            logging.getLogger(__name__).debug('save_frame makeImageSnapshot failed idx=%s path=%s error=%r', idx, path, e)
                            img = None

                        b = None
                        if img is not None:
                            try:
                                data = img.encodeToData()
                                if data is not None:
                                    if hasattr(data, 'toBytes'):
                                        b = data.toBytes()
                                    elif hasattr(data, 'tobytes'):
                                        b = data.tobytes()
                                    else:
                                        b = bytes(data)
                            except Exception as e:
                                logging.getLogger(__name__).debug('save_frame encode failed idx=%s path=%s error=%r', idx, path, e)
                                b = None

                        # GL readback fallback
                        if not b:
                            try:
                                from pyglet import gl as _gl
                                from PIL import Image as _Image
                                # Prefer device-pixel surface/backing size for readback
                                try:
                                    w, h = getattr(self, '_surface_size') or getattr(self, '_backing_size')
                                except Exception:
                                    try:
                                        w, h = getattr(self, '_backing_size')
                                    except Exception:
                                        w = int(self.width)
                                        h = int(self.height)
                                try:
                                    logging.getLogger(__name__).debug('save_frame glReadPixels using w=%d h=%d fbo=%s', w, h, getattr(self, 'fbo_id', None))
                                    try:
                                        # Mirror this diagnostic to /tmp for easier inspection in headless runs
                                        with open('/tmp/pycreative_saveframe_debug.txt', 'a') as _df:
                                            _df.write(f'save_frame glReadPixels using w={w} h={h} fbo={getattr(self, "fbo_id", None)}\n')
                                    except Exception:
                                        pass
                                except Exception:
                                    pass
                                _gl.glBindFramebuffer(_gl.GL_FRAMEBUFFER, int(self.fbo_id or 0))
                                buf = (ctypes.c_ubyte * (w * h * 4))()
                                # Ensure pack alignment is 1 for tightly-packed RGBA rows
                                try:
                                    _gl.glPixelStorei(_gl.GL_PACK_ALIGNMENT, 1)
                                except Exception:
                                    pass
                                try:
                                    _gl.glReadPixels(0, 0, w, h, _gl.GL_RGBA, _gl.GL_UNSIGNED_BYTE, ctypes.byref(buf))
                                finally:
                                    try:
                                        _gl.glPixelStorei(_gl.GL_PACK_ALIGNMENT, 4)
                                    except Exception:
                                        pass
                                raw = bytes(buf)
                                # Diagnostic: record raw readback length and expected size
                                try:
                                    rb_len = len(raw)
                                    expect = int(w) * int(h) * 4
                                    try:
                                        with open('/tmp/pycreative_present_readbacks.log', 'a') as _rf:
                                            _rf.write(f'{time.time():.6f} save_frame glReadPixels raw_bytes={rb_len} expected={expect} w={w} h={h} fbo={getattr(self, "fbo_id", None)}\n')
                                    except Exception:
                                        pass
                                    try:
                                        logging.getLogger(__name__).debug('save_frame glReadPixels raw_bytes=%d expected=%d w=%d h=%d fbo=%s', rb_len, expect, w, h, getattr(self, 'fbo_id', None))
                                    except Exception:
                                        pass
                                except Exception:
                                    pass
                                try:
                                    # Debug: record what arguments we will pass to Pillow.frombytes
                                    try:
                                        rb_len = len(raw)
                                    except Exception:
                                        rb_len = None
                                    try:
                                        expect = int(w) * int(h) * 4
                                    except Exception:
                                        expect = None
                                    msg = f'FROMBYTES_CALL: tag=save_frame w={w} h={h} rb_len={rb_len} expect={expect}'
                                    try:
                                        logging.getLogger(__name__).debug(msg)
                                    except Exception:
                                        pass
                                    try:
                                        with open('/tmp/pycreative_frombytes_debug.log', 'a') as _fb:
                                            _fb.write(msg + '\n')
                                    except Exception:
                                        pass
                                except Exception:
                                    pass

                                # Only call Pillow.frombytes when the raw buffer length
                                # matches the expected size for (w,h). If it doesn't match
                                # try to infer a correct (w,h) from common candidates
                                # (surface/backing/logical) so we avoid interpreting a
                                # 400x400 buffer as 200x200 which produced the half-size
                                # quadrant artifact during debugging.
                                try:
                                    rb_len = len(raw)
                                except Exception:
                                    rb_len = None
                                inferred_w = w
                                inferred_h = h
                                expect = None
                                try:
                                    expect = int(inferred_w) * int(inferred_h) * 4
                                except Exception:
                                    expect = None
                                if rb_len is not None and expect is not None and rb_len != expect:
                                    # Candidates to try: surface_size, backing_size, presenter's logical size
                                    candidates = []
                                    try:
                                        candidates.append(getattr(self, '_surface_size'))
                                    except Exception:
                                        pass
                                    try:
                                        candidates.append(getattr(self, '_backing_size'))
                                    except Exception:
                                        pass
                                    try:
                                        candidates.append(getattr(self, '_logical_size'))
                                    except Exception:
                                        pass
                                    try:
                                        candidates.append((int(self.width), int(self.height)))
                                    except Exception:
                                        pass
                                    found = False
                                    for cand in candidates:
                                        try:
                                            if not cand:
                                                continue
                                            cw, ch = int(cand[0]), int(cand[1])
                                            if cw * ch * 4 == rb_len:
                                                inferred_w, inferred_h = cw, ch
                                                found = True
                                                try:
                                                    logging.getLogger(__name__).debug('FROMBYTES_CALL: inferred dims for save_frame -> %dx%d (rb_len=%d)', inferred_w, inferred_h, rb_len)
                                                except Exception:
                                                    pass
                                                try:
                                                    with open('/tmp/pycreative_frombytes_debug.log', 'a') as _fb:
                                                        _fb.write(f'INFERRED_SAVE_FRAME w={inferred_w} h={inferred_h} rb_len={rb_len}\n')
                                                except Exception:
                                                    pass
                                                break
                                        except Exception:
                                            continue
                                    if not found:
                                        try:
                                            logging.getLogger(__name__).debug('FROMBYTES_CALL: unable to infer valid dims for save_frame rb_len=%r w=%r h=%r', rb_len, w, h)
                                        except Exception:
                                            pass
                                        # Skip this save_frame write to avoid corrupt output
                                        raise RuntimeError('raw readback size mismatch; skipping save_frame')

                                img_p = _Image.frombytes('RGBA', (int(inferred_w), int(inferred_h)), raw)
                                img_p = img_p.transpose(_Image.FLIP_TOP_BOTTOM)
                                import io as _io
                                bio = _io.BytesIO()
                                img_p.save(bio, 'PNG')
                                b = bio.getvalue()
                            except Exception as e:
                                logging.getLogger(__name__).debug('save_frame glReadPixels failed idx=%s path=%s error=%r', idx, path, e)
                                b = None

                        if not b:
                            logging.getLogger(__name__).debug('save_frame no bytes obtained idx=%s path=%s', idx, path)
                            continue

                        # Write atomically: create a temp file next to the target
                        # and replace the final path. This avoids noisy /tmp files
                        # and ensures an atomic move where supported.
                        try:
                            import tempfile as _tempfile
                            import os as _os
                            dirn = _os.path.dirname(path) or '.'
                            fd, tmp_out = _tempfile.mkstemp(suffix='.png', dir=dirn)
                            try:
                                with os.fdopen(fd, 'wb') as _tf:
                                    _tf.write(b)
                                # Replace the target atomically
                                _os.replace(tmp_out, path)
                                logging.getLogger(__name__).info('wrote save_frame to %s', path)
                            except Exception as e:
                                # Cleanup tmp file if it still exists
                                try:
                                    if _os.path.exists(tmp_out):
                                        _os.remove(tmp_out)
                                except Exception:
                                    pass
                                logging.getLogger(__name__).debug('save_frame final write failed idx=%s path=%s error=%r', idx, path, e)
                                continue
                        except Exception as e:
                            logging.getLogger(__name__).debug('save_frame atomic write setup failed idx=%s path=%s error=%r', idx, path, e)
                            continue
                    except Exception:
                        logging.getLogger(__name__).debug('save_frame unexpected handler error idx=%s path=%s', idx, path)
                        continue
                except Exception:
                    # ignore per-command errors
                    pass
        except Exception:
            pass

        # Debug-only: optionally write a PNG snapshot of the Skia surface to disk
        # to verify that drawing occurred. Enabled with PYCREATIVE_DEBUG_LIFECYCLE_DUMP=1
        try:
            if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE_DUMP', '') == '1':
                try:
                    # surf is a skia.Surface; makeImageSnapshot returns an Image
                    try:
                        img = surf.makeImageSnapshot()
                    except Exception as e:
                        logging.getLogger(__name__).debug('makeImageSnapshot() raised %r', repr(e))
                        img = None

                    if img is None:
                        logging.getLogger(__name__).debug('makeImageSnapshot() returned None')
                    else:
                        data = None
                        try:
                            # Prefer the no-arg encodeToData() which many skia builds
                            # implement and which returns a skia.Data wrapper.
                            data = img.encodeToData()
                        except Exception as e:
                            logging.getLogger(__name__).debug('img.encodeToData() raised %r', repr(e))
                            data = None

                        if data is None:
                            logging.getLogger(__name__).debug('encodeToData returned None; falling back to glReadPixels')
                            # Fallback: read pixels from the bound FBO using glReadPixels.
                            # Use device-pixel backing/surface size when possible.
                            try:
                                from pyglet import gl as _gl
                                import io as _io
                                from PIL import Image as _Image

                                # Diagnostic: report what is attached to the FBO before readback
                                try:
                                    if hasattr(_gl, 'glGetFramebufferAttachmentParameteriv'):
                                        try:
                                            atype = _gl.GLint()
                                            aname = _gl.GLint()
                                            _gl.glGetFramebufferAttachmentParameteriv(_gl.GL_FRAMEBUFFER, _gl.GL_COLOR_ATTACHMENT0, _gl.GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE, ctypes.byref(atype))
                                            _gl.glGetFramebufferAttachmentParameteriv(_gl.GL_FRAMEBUFFER, _gl.GL_COLOR_ATTACHMENT0, _gl.GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME, ctypes.byref(aname))
                                            logging.getLogger(__name__).debug('FBO attachment object_type=%s object_name=%s', int(atype.value), int(aname.value))
                                        except Exception as e:
                                            logging.getLogger(__name__).debug('FBO attachment query raised %r', repr(e))
                                except Exception:
                                    pass

                                try:
                                    # Ensure our FBO is bound (we bound earlier when using_gpu)
                                    _gl.glBindFramebuffer(_gl.GL_FRAMEBUFFER, int(self.fbo_id or 0))
                                except Exception:
                                    # binding failed; continue and attempt readpixels anyway
                                    pass

                                try:
                                    try:
                                        w, h = getattr(self, '_surface_size') or getattr(self, '_backing_size')
                                    except Exception:
                                        try:
                                            w, h = getattr(self, '_backing_size')
                                        except Exception:
                                            w = int(self.width)
                                            h = int(self.height)
                                    # Read pixels into a ctypes buffer (RGBA)
                                    buf = (ctypes.c_ubyte * (w * h * 4))()
                                    _gl.glReadPixels(0, 0, w, h, _gl.GL_RGBA, _gl.GL_UNSIGNED_BYTE, ctypes.byref(buf))
                                    raw = bytes(buf)
                                    # Diagnostic: record raw readback length and expected size
                                    try:
                                        rb_len = len(raw)
                                        expect = int(w) * int(h) * 4
                                        try:
                                            with open('/tmp/pycreative_present_readbacks.log', 'a') as _rf:
                                                _rf.write(f'debug_frame glReadPixels raw_bytes={rb_len} expected={expect} w={w} h={h} fbo={getattr(self, "fbo_id", None)}\n')
                                        except Exception:
                                            pass
                                        try:
                                            logging.getLogger(__name__).debug('debug glReadPixels raw_bytes=%d expected=%d w=%d h=%d fbo=%s', rb_len, expect, w, h, getattr(self, 'fbo_id', None))
                                        except Exception:
                                            pass
                                    except Exception:
                                        pass
                                    try:
                                        # Debug: record what arguments we will pass to Pillow.frombytes
                                        try:
                                            rb_len = len(raw)
                                        except Exception:
                                            rb_len = None
                                        try:
                                            expect = int(w) * int(h) * 4
                                        except Exception:
                                            expect = None
                                        msg = f'FROMBYTES_CALL: tag=debug_frame_fallback w={w} h={h} rb_len={rb_len} expect={expect}'
                                        try:
                                            logging.getLogger(__name__).debug(msg)
                                        except Exception:
                                            pass
                                        try:
                                            with open('/tmp/pycreative_frombytes_debug.log', 'a') as _fb:
                                                _fb.write(msg + '\n')
                                        except Exception:
                                            pass
                                    except Exception:
                                        pass

                                    try:
                                        rb_len = len(raw)
                                    except Exception:
                                        rb_len = None
                                    inferred_w = w
                                    inferred_h = h
                                    expect = None
                                    try:
                                        expect = int(inferred_w) * int(inferred_h) * 4
                                    except Exception:
                                        expect = None
                                    if rb_len is not None and expect is not None and rb_len != expect:
                                        # Try to infer correct dims from common candidates
                                        candidates = []
                                        try:
                                            candidates.append(getattr(self, '_surface_size'))
                                        except Exception:
                                            pass
                                        try:
                                            candidates.append(getattr(self, '_backing_size'))
                                        except Exception:
                                            pass
                                        try:
                                            candidates.append(getattr(self, '_logical_size'))
                                        except Exception:
                                            pass
                                        try:
                                            candidates.append((int(self.width), int(self.height)))
                                        except Exception:
                                            pass
                                        found = False
                                        for cand in candidates:
                                            try:
                                                if not cand:
                                                    continue
                                                cw, ch = int(cand[0]), int(cand[1])
                                                if cw * ch * 4 == rb_len:
                                                    inferred_w, inferred_h = cw, ch
                                                    found = True
                                                    try:
                                                        logging.getLogger(__name__).debug('FROMBYTES_CALL: inferred dims for debug_frame_fallback -> %dx%d (rb_len=%d)', inferred_w, inferred_h, rb_len)
                                                    except Exception:
                                                        pass
                                                    try:
                                                        with open('/tmp/pycreative_frombytes_debug.log', 'a') as _fb:
                                                            _fb.write(f'INFERRED_DEBUG_FRAME w={inferred_w} h={inferred_h} rb_len={rb_len}\n')
                                                    except Exception:
                                                        pass
                                                    break
                                            except Exception:
                                                continue
                                        if not found:
                                            try:
                                                logging.getLogger(__name__).debug('FROMBYTES_CALL: unable to infer valid dims for debug_frame rb_len=%r w=%r h=%r', rb_len, w, h)
                                            except Exception:
                                                pass
                                            raise RuntimeError('raw readback size mismatch; skipping debug_frame snapshot')

                                    img_p = _Image.frombytes('RGBA', (int(inferred_w), int(inferred_h)), raw)
                                    img_p = img_p.transpose(_Image.FLIP_TOP_BOTTOM)
                                    bio = _io.BytesIO()
                                    img_p.save(bio, 'PNG')
                                    png_bytes = bio.getvalue()
                                    path = '/tmp/pycreative_debug_frame.png'
                                    with open(path, 'wb') as f:
                                        f.write(png_bytes)
                                    logging.getLogger(__name__).debug('wrote Skia snapshot (glReadPixels) to %s', path)
                                except Exception as e:
                                    logging.getLogger(__name__).debug('glReadPixels -> Pillow failed %r', repr(e))
                            except Exception as e:
                                logging.getLogger(__name__).debug('glReadPixels fallback unavailable %r', repr(e))
                        else:
                            b = None
                            try:
                                # skia.Data may support toBytes or tobytes/tobytes
                                if hasattr(data, 'toBytes'):
                                    b = data.toBytes()
                                elif hasattr(data, 'tobytes'):
                                    b = data.tobytes()
                                elif hasattr(data, 'tobytes'):
                                    b = data.tobytes()
                                else:
                                    try:
                                        b = bytes(data)
                                    except Exception:
                                        b = None
                            except Exception as e:
                                logging.getLogger(__name__).debug('extracting bytes from skia.Data raised %r', repr(e))
                                b = None

                            if not b:
                                logging.getLogger(__name__).debug('no bytes extracted from encoded data')
                            else:
                                path = '/tmp/pycreative_debug_frame.png'
                                try:
                                    with open(path, 'wb') as f:
                                        f.write(b)
                                    logging.getLogger(__name__).debug('wrote Skia snapshot to %s', path)
                                except Exception as e:
                                    logging.getLogger(__name__).debug('failed writing snapshot %r', repr(e))
                except Exception as e:
                    logging.getLogger(__name__).debug('snapshot dump internal error %r', repr(e))
        except Exception:
            pass

        # Unbind FBO if we bound it
        if using_gpu:
            try:
                from pyglet import gl
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            except Exception:
                pass

        return surf

    def present(self):
        # Simpler, robust present implementation with minimal nesting so
        # syntax errors are less likely and diagnostics are still emitted.
        from pyglet import gl

        # Query drawable size (viewport) if available
        try:
            vp = (gl.GLint * 4)()
            gl.glGetIntegerv(gl.GL_VIEWPORT, vp)
            vw = int(vp[2])
            vh = int(vp[3])
        except Exception:
            vw = None
            vh = None

        # If the drawable size differs from our presenter logical size,
        # resize now and ask the caller to re-render once at the correct
        # device-pixel size by returning True.
        if vw and vh and (int(getattr(self, 'width', 0)) != vw or int(getattr(self, 'height', 0)) != vh):
            try:
                logging.getLogger(__name__).debug('present early-detect: viewport %s,%s != presenter %s,%s; resizing', vw, vh, getattr(self, 'width', None), getattr(self, 'height', None))
            except Exception:
                pass
            try:
                self.resize(int(vw), int(vh))
                return True
            except Exception:
                pass

        # Try a framebuffer blit (preferred); fall back to a simple bind+no-op
        # if blit is unavailable or fails.
        try:
            try:
                gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, int(self.fbo_id))
                gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)
            except Exception:
                try:
                    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, int(self.fbo_id))
                except Exception:
                    pass

            if hasattr(gl, 'glBlitFramebuffer'):
                try:
                    # Source (FBO / Skia surface) size should be the device-pixel
                    # backing size the texture/FBO was allocated with. Prefer the
                    # actual Skia surface size, falling back to the recorded
                    # backing size or the presenter's logical size.
                    try:
                        src_w, src_h = getattr(self, '_surface_size') or getattr(self, '_backing_size')
                    except Exception:
                        try:
                            src_w, src_h = getattr(self, '_backing_size')
                        except Exception:
                            src_w, src_h = int(self.width), int(self.height)
                    dst_w = int(vw) if vw is not None else int(self.width)
                    dst_h = int(vh) if vh is not None else int(self.height)
                    gl.glBlitFramebuffer(0, 0, int(src_w), int(src_h), 0, 0, dst_w, dst_h, gl.GL_COLOR_BUFFER_BIT, gl.GL_NEAREST)
                    try:
                        self._last_present_mode = 'blit'
                    except Exception:
                        pass
                except Exception as e:
                    try:
                        logging.getLogger(__name__).debug('present: glBlitFramebuffer raised %r', repr(e))
                    except Exception:
                        pass
            else:
                try:
                    # No blit available; attempt to bind back to default
                    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
                except Exception:
                    pass
        finally:
            try:
                gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, 0)
            except Exception:
                try:
                    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
                except Exception:
                    pass

        # Lightweight diagnostics (short line and JSON record) for offline analysis
        try:
            if os.getenv('PYCREATIVE_DEBUG_PRESENT', '') == '1':
                try:
                    from pyglet import gl as _gl
                    try:
                        _err = int(_gl.glGetError())
                    except Exception:
                        _err = None
                except Exception:
                    _err = None
                try:
                    print(f'PRESENTER DEBUG: mode={getattr(self, "_last_present_mode", None)} glError={_err}')
                except Exception:
                    pass
                try:
                    with open('/tmp/pycreative_present_log.txt', 'a') as _f:
                        _f.write(f'mode={getattr(self, "_last_present_mode", None)} glError={_err}\n')
                except Exception:
                    pass
                try:
                    full = {
                        'ts': time.time(),
                        'present_mode': getattr(self, '_last_present_mode', None),
                        'viewport_w': int(vw) if vw is not None else None,
                        'viewport_h': int(vh) if vh is not None else None,
                        'presenter_width': int(getattr(self, 'width', None)) if getattr(self, 'width', None) is not None else None,
                        'presenter_height': int(getattr(self, 'height', None)) if getattr(self, 'height', None) is not None else None,
                        'backing_size': getattr(self, '_backing_size', None),
                        'surface_size': getattr(self, '_surface_size', None),
                        'tex_id': int(getattr(self, 'tex_id', None)) if getattr(self, 'tex_id', None) is not None else None,
                        'fbo_id': int(getattr(self, 'fbo_id', None)) if getattr(self, 'fbo_id', None) is not None else None,
                    }
                    try:
                        with open('/tmp/pycreative_present_full_diagnostics.log', 'a') as _f:
                            _f.write(json.dumps(full) + '\n')
                    except Exception:
                        pass
                except Exception:
                    pass
        except Exception:
            pass

        # Optional post-present framebuffer dump for visual verification
        try:
            if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE_DUMP', '') == '1':
                try:
                    from pyglet import gl as _gl
                    w = int(vw) if vw is not None else int(self.width)
                    h = int(vh) if vh is not None else int(self.height)
                    buf = (_gl.GLubyte * (w * h * 4))()
                    _gl.glBindFramebuffer(_gl.GL_FRAMEBUFFER, 0)
                    _gl.glReadPixels(0, 0, w, h, _gl.GL_RGBA, _gl.GL_UNSIGNED_BYTE, buf)
                    raw = bytes(buf)
                    from PIL import Image as _Image
                    try:
                        # Debug: record what arguments we will pass to Pillow.frombytes
                        try:
                            rb_len = len(raw)
                        except Exception:
                            rb_len = None
                        try:
                            expect = int(w) * int(h) * 4
                        except Exception:
                            expect = None
                        msg = f'FROMBYTES_CALL: tag=post_present w={w} h={h} rb_len={rb_len} expect={expect}'
                        try:
                            logging.getLogger(__name__).debug(msg)
                        except Exception:
                            pass
                        try:
                            with open('/tmp/pycreative_frombytes_debug.log', 'a') as _fb:
                                _fb.write(msg + '\n')
                        except Exception:
                            pass
                    except Exception:
                        pass
                    try:
                        rb_len = len(raw)
                    except Exception:
                        rb_len = None
                    inferred_w = w
                    inferred_h = h
                    expect = None
                    try:
                        expect = int(inferred_w) * int(inferred_h) * 4
                    except Exception:
                        expect = None
                    if rb_len is not None and expect is not None and rb_len != expect:
                        candidates = []
                        try:
                            candidates.append(getattr(self, '_surface_size'))
                        except Exception:
                            pass
                        try:
                            candidates.append(getattr(self, '_backing_size'))
                        except Exception:
                            pass
                        try:
                            candidates.append(getattr(self, '_logical_size'))
                        except Exception:
                            pass
                        try:
                            candidates.append((int(self.width), int(self.height)))
                        except Exception:
                            pass
                        found = False
                        for cand in candidates:
                            try:
                                if not cand:
                                    continue
                                cw, ch = int(cand[0]), int(cand[1])
                                if cw * ch * 4 == rb_len:
                                    inferred_w, inferred_h = cw, ch
                                    found = True
                                    try:
                                        logging.getLogger(__name__).debug('FROMBYTES_CALL: inferred dims for post_present -> %dx%d (rb_len=%d)', inferred_w, inferred_h, rb_len)
                                    except Exception:
                                        pass
                                    try:
                                        with open('/tmp/pycreative_frombytes_debug.log', 'a') as _fb:
                                            _fb.write(f'INFERRED_POST_PRESENT w={inferred_w} h={inferred_h} rb_len={rb_len}\n')
                                    except Exception:
                                        pass
                                    break
                            except Exception:
                                continue
                        if not found:
                            try:
                                logging.getLogger(__name__).debug('FROMBYTES_CALL: unable to infer valid dims for post_present rb_len=%r w=%r h=%r', rb_len, w, h)
                            except Exception:
                                pass
                            raise RuntimeError('raw readback size mismatch; skipping post_present snapshot')

                    img_p = _Image.frombytes('RGBA', (int(inferred_w), int(inferred_h)), raw)
                    img_p = img_p.transpose(_Image.FLIP_TOP_BOTTOM)
                    path = '/tmp/pycreative_post_present.png'
                    img_p.save(path, 'PNG')
                    try:
                        logging.getLogger(__name__).debug('wrote post-present snapshot to %s', path)
                    except Exception:
                        pass
                except Exception:
                    try:
                        logging.getLogger(__name__).debug('post-present readback failed')
                    except Exception:
                        pass
        except Exception:
            pass

        return False

    def replay_fn(self, commands, canvas):
        # Delegate to the centralized replayer which handles transforms
        # and shape commands consistently across offscreen and GPU paths.
        try:
            from core.io.replay_to_skia_impl import replay_to_skia_canvas
        except Exception:
            # If we can't import the centralized replayer, log when
            # debugging and return (the caller may provide other fallbacks).
            try:
                import os
                import logging
                import traceback
                if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                    logging.getLogger(__name__).debug('presenter.replay_fn: failed to import core.io.replay_to_skia_impl')
                    traceback.print_exc()
            except Exception:
                pass
            return

        try:
            try:
                import os
                import logging
                if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                    logging.getLogger(__name__).debug('presenter.replay_fn: delegating to replay_to_skia_canvas')
            except Exception:
                pass
            replay_to_skia_canvas(commands, canvas)
        except Exception:
            # If the delegate raises, log the traceback when debugging
            # so we can diagnose problems in the replayer implementation.
            try:
                import os
                import logging
                import traceback
                if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                    logging.getLogger(__name__).debug('presenter.replay_fn: replay_to_skia_canvas raised an exception')
                    traceback.print_exc()
            except Exception:
                pass

    def teardown(self):
        # Make teardown idempotent: multiple calls are safe and will be
        # no-ops after the first. This avoids duplicate debug noise and
        # repeated GL resource deletion attempts.
        if getattr(self, '_teardown_done', False):
            return
        try:
            self._teardown_done = True
        except Exception:
            pass

        from pyglet import gl
        try:
            if self.tex_id is not None:
                t = gl.GLuint(int(self.tex_id))
                gl.glDeleteTextures(1, ctypes.byref(t))
                self.tex_id = None
        except Exception:
            pass
        try:
            if self.fbo_id is not None:
                f = gl.GLuint(int(self.fbo_id))
                gl.glDeleteFramebuffers(1, ctypes.byref(f))
                self.fbo_id = None
        except Exception:
            pass
        try:
            if self.gr_context is not None:
                if hasattr(self.gr_context, 'abandonContext'):
                    self.gr_context.abandonContext()
                elif hasattr(self.gr_context, 'releaseResourcesAndAbandonContext'):
                    self.gr_context.releaseResourcesAndAbandonContext()
                self.gr_context = None
        except Exception:
            pass

        # delete textured-quad GL program/VBO if present
        try:
            if getattr(self, '_fs_vbo', None) is not None:
                v = gl.GLuint(int(self._fs_vbo))
                try:
                    gl.glDeleteBuffers(1, ctypes.byref(v))
                except Exception:
                    pass
                self._fs_vbo = None
        except Exception:
            pass
        try:
            if getattr(self, '_fs_vao', None) is not None:
                try:
                    vao = gl.GLuint(int(self._fs_vao))
                    gl.glDeleteVertexArrays(1, ctypes.byref(vao))
                except Exception:
                    try:
                        # some drivers expose alternative symbol names
                        gl.glDeleteVertexArraysAPPLE
                    except Exception:
                        pass
                self._fs_vao = None
        except Exception:
            pass
        try:
            if getattr(self, '_fs_prog', None) is not None:
                try:
                    gl.glDeleteProgram(int(self._fs_prog))
                except Exception:
                    pass
                self._fs_prog = None
        except Exception:
            pass

    def resize(self, width: int, height: int):
        """Resize the presenter's backing texture/FBO and drop any Skia surface.

        This tears down existing GL and Skia resources; caller should then
        call ensure_resources()/create_skia_surface() via render_commands.
        """
        try:
            # delete GL resources if present
            from pyglet import gl
            if self.tex_id is not None:
                t = gl.GLuint(int(self.tex_id))
                try:
                    gl.glDeleteTextures(1, ctypes.byref(t))
                except Exception:
                    pass
                self.tex_id = None
        except Exception:
            pass
        try:
            from pyglet import gl
            if self.fbo_id is not None:
                f = gl.GLuint(int(self.fbo_id))
                try:
                    gl.glDeleteFramebuffers(1, ctypes.byref(f))
                except Exception:
                    pass
                self.fbo_id = None
        except Exception:
            pass
        # drop Skia surface/context so create_skia_surface will recreate
        try:
            if self.gr_context is not None:
                if hasattr(self.gr_context, 'abandonContext'):
                    self.gr_context.abandonContext()
                elif hasattr(self.gr_context, 'releaseResourcesAndAbandonContext'):
                    self.gr_context.releaseResourcesAndAbandonContext()
        except Exception:
            pass
        self.gr_context = None
        self.surface = None
        self.width = int(width)
        self.height = int(height)
        # drop textured-quad resources so they'll be recreated if needed
        try:
            if getattr(self, '_fs_vbo', None) is not None:
                from pyglet import gl
                v = gl.GLuint(int(self._fs_vbo))
                try:
                    gl.glDeleteBuffers(1, ctypes.byref(v))
                except Exception:
                    pass
                self._fs_vbo = None
        except Exception:
            pass
        try:
            self._fs_prog = None
        except Exception:
            pass
        try:
            self._fs_vao = None
        except Exception:
            pass

    # --- textured-quad (VBO + GLSL 1.20) helpers ---
    def _compile_shader(self, source: str, shader_type):
        from pyglet import gl
        # Ensure version directive (if present) is at the start by stripping
        # any leading whitespace or BOM characters. Some drivers are strict
        # about #version placement.
        try:
            source = source.lstrip()
        except Exception:
            pass
        src_buf = ctypes.create_string_buffer(source.encode('utf-8'))
        src_ptr = ctypes.cast(ctypes.pointer(ctypes.pointer(src_buf)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, 1, src_ptr, None)
        gl.glCompileShader(shader)
        status = gl.GLint()
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ctypes.byref(status))
        if not bool(status.value):
            # retrieve info log
            log_len = gl.GLint()
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, ctypes.byref(log_len))
            if log_len.value > 0:
                buf = ctypes.create_string_buffer(log_len.value)
                gl.glGetShaderInfoLog(shader, log_len.value, None, buf)
                msg = buf.value.decode('utf-8', 'ignore')
                try:
                    logging.getLogger(__name__).debug('VBO shader compile log: %s', msg)
                except Exception:
                    pass
                raise RuntimeError('Shader compile error: ' + msg)
            raise RuntimeError('Shader compile failed')
        return shader

    def _link_program(self, vert, frag, bind_attribs=None):
        from pyglet import gl
        prog = gl.glCreateProgram()
        gl.glAttachShader(prog, vert)
        gl.glAttachShader(prog, frag)
        if bind_attribs:
            for idx, name in enumerate(bind_attribs):
                try:
                    # prefer bytes for older bindings
                    gl.glBindAttribLocation(prog, int(idx), name.encode('utf-8'))
                except Exception:
                    try:
                        gl.glBindAttribLocation(prog, int(idx), name)
                    except Exception:
                        pass
        gl.glLinkProgram(prog)
        status = gl.GLint()
        gl.glGetProgramiv(prog, gl.GL_LINK_STATUS, ctypes.byref(status))
        if not bool(status.value):
            log_len = gl.GLint()
            gl.glGetProgramiv(prog, gl.GL_INFO_LOG_LENGTH, ctypes.byref(log_len))
            if log_len.value > 0:
                buf = ctypes.create_string_buffer(log_len.value)
                gl.glGetProgramInfoLog(prog, log_len.value, None, buf)
                msg = buf.value.decode('utf-8', 'ignore')
                try:
                    logging.getLogger(__name__).debug('VBO program link log: %s', msg)
                except Exception:
                    pass
                raise RuntimeError('Program link error: ' + msg)
            raise RuntimeError('Program link failed')
        return prog

    def _ensure_textured_quad_resources(self):
        """Create GLSL 1.20 program and a static VBO for a fullscreen quad."""
        if getattr(self, '_fs_prog', None) is not None and getattr(self, '_fs_vbo', None) is not None:
            return
        from pyglet import gl

        # Try modern GLSL first (core-profile friendly), then fall back to
        # legacy GLSL 1.20 if needed.
        vert = None
        frag = None
        prog = None
        tried_variants = []
        # GLSL 150 (modern core) variant
        vs150 = '''#version 150
in vec2 a_pos;
in vec2 a_uv;
out vec2 v_uv;
uniform float u_flip_y;
void main() {
    v_uv = a_uv;
    if (u_flip_y < 0.5) {
        v_uv.y = 1.0 - v_uv.y;
    }
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
'''
        fs150 = '''#version 150
in vec2 v_uv;
out vec4 fragColor;
uniform sampler2D u_tex;
void main() {
    vec4 c = texture(u_tex, v_uv);
    fragColor = c;
}
'''

        # GLES 3.0 (GLSL ES 300) variant for OpenGL ES 3 contexts
        vs_es300 = '''#version 300 es
in vec2 a_pos;
in vec2 a_uv;
out vec2 v_uv;
uniform float u_flip_y;
void main() {
    v_uv = a_uv;
    if (u_flip_y < 0.5) {
        v_uv.y = 1.0 - v_uv.y;
    }
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
'''
        fs_es300 = '''#version 300 es
precision mediump float;
in vec2 v_uv;
uniform sampler2D u_tex;
out vec4 fragColor;
void main() {
    vec4 c = texture(u_tex, v_uv);
    fragColor = c;
}
'''

        # GLSL 1.20 legacy variant
        vs120 = '''#version 120
attribute vec2 a_pos;
attribute vec2 a_uv;
varying vec2 v_uv;
uniform float u_flip_y;
void main() {
    v_uv = a_uv;
    if (u_flip_y < 0.5) {
        v_uv.y = 1.0 - v_uv.y;
    }
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
'''
        fs120 = '''#version 120
varying vec2 v_uv;
uniform sampler2D u_tex;
void main() {
    vec4 c = texture2D(u_tex, v_uv);
    gl_FragColor = c;
}
'''

        # Decide ordering: if force_gles is set or sniffing indicates GLES3,
        # prefer the ES300 variant first, otherwise try desktop 150 then 120.
        variants = []
        try:
            prefer_es = bool(self.force_gles) or self._sniff_gles3_support()
        except Exception:
            prefer_es = bool(self.force_gles)
        if prefer_es:
            variants.extend([
                ('es300', vs_es300, fs_es300),
                ('150', vs150, fs150),
                ('120', vs120, fs120),
            ])
        else:
            variants.extend([
                ('150', vs150, fs150),
                ('es300', vs_es300, fs_es300),
                ('120', vs120, fs120),
            ])
        last_exc = None
        for tag, vs_src, fs_src in variants:
            tried_variants.append(tag)
            try:
                vert = self._compile_shader(vs_src, gl.GL_VERTEX_SHADER)
                frag = self._compile_shader(fs_src, gl.GL_FRAGMENT_SHADER)
                # For modern GLSL we can still bind attributes before link
                prog = self._link_program(vert, frag, bind_attribs=['a_pos', 'a_uv'])
                try:
                    logging.getLogger(__name__).debug('Compiled shader variant GLSL %s', tag)
                except Exception:
                    pass
                break
            except Exception as e:
                last_exc = e
                try:
                    if vert is not None:
                        gl.glDeleteShader(vert)
                except Exception:
                    pass
                try:
                    if frag is not None:
                        gl.glDeleteShader(frag)
                except Exception:
                    pass
                vert = None
                frag = None
                prog = None
                continue
        if prog is None:
            # re-raise last exception to signal failure to caller
            if last_exc is not None:
                raise last_exc
            raise RuntimeError('Failed to compile any shader variant')

        # locate uniforms and attrib bindings
        try:
            self._fs_prog = int(prog)
            loc_tex = gl.glGetUniformLocation(prog, b'u_tex')
            loc_flip = gl.glGetUniformLocation(prog, b'u_flip_y')
            self._fs_prog_u_tex = int(loc_tex) if loc_tex is not None else None
            self._fs_prog_u_flip = int(loc_flip) if loc_flip is not None else None
            # attribute indices for GLSL 1.20 were bound in _link_program
            self._fs_prog_attrib_pos = 0
            self._fs_prog_attrib_uv = 1
        except Exception:
            self._fs_prog = None
            raise

        # create VBO with 6 verts (two triangles), interleaved pos.xy, uv.xy
        import array
        verts = array.array('f', [
            -1.0, -1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 0.0,
             1.0,  1.0, 1.0, 1.0,
            -1.0, -1.0, 0.0, 0.0,
             1.0,  1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 1.0,
        ])

        vbo = gl.GLuint()
        gl.glGenBuffers(1, ctypes.byref(vbo))
        self._fs_vbo = int(vbo.value)
        try:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, int(self._fs_vbo))
            size = ctypes.sizeof(ctypes.c_float) * len(verts)
            # create ctypes array from python array
            ptr = (ctypes.c_float * len(verts))(*verts)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, size, ctypes.byref(ptr), gl.GL_STATIC_DRAW)
        finally:
            try:
                gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
            except Exception:
                pass

        # Create and populate a VAO if available (required by core profiles)
        try:
            if hasattr(gl, 'glGenVertexArrays') and hasattr(gl, 'glBindVertexArray'):
                vao = gl.GLuint()
                gl.glGenVertexArrays(1, ctypes.byref(vao))
                self._fs_vao = int(vao.value)
                try:
                    gl.glBindVertexArray(int(self._fs_vao))
                    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, int(self._fs_vbo))
                    stride = ctypes.sizeof(ctypes.c_float) * 4
                    try:
                        gl.glEnableVertexAttribArray(self._fs_prog_attrib_pos)
                        gl.glVertexAttribPointer(self._fs_prog_attrib_pos, 2, gl.GL_FLOAT, False, stride, ctypes.c_void_p(0))
                        gl.glEnableVertexAttribArray(self._fs_prog_attrib_uv)
                        gl.glVertexAttribPointer(self._fs_prog_attrib_uv, 2, gl.GL_FLOAT, False, stride, ctypes.c_void_p(ctypes.sizeof(ctypes.c_float) * 2))
                    except Exception:
                        pass
                finally:
                    try:
                        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
                    except Exception:
                        pass
                    try:
                        gl.glBindVertexArray(0)
                    except Exception:
                        pass
        except Exception:
            # VAO not available or creation failed; continue without it
            try:
                self._fs_vao = None
            except Exception:
                pass
        # Diagnostic: print created resource IDs and any GL error
        try:
            try:
                logging.getLogger(__name__).debug('VBO created prog=%r vbo=%r vao=%r', self._fs_prog, self._fs_vbo, self._fs_vao)
            except Exception:
                pass
            try:
                err = int(gl.glGetError())
                if err != 0:
                    logging.getLogger(__name__).debug('VBO glGetError after resource create: %r', err)
            except Exception:
                pass
        except Exception:
            pass

        # Save-frame processing is handled earlier in this function; the
        # implementation below was refactored to a single location to avoid
        # duplication. Leave a quiet marker in the log to aid debugging.
        try:
            logging.getLogger(__name__).debug('save_frame processing merged into render_commands')
        except Exception:
            pass

    def _draw_textured_quad_vbo(self, tex_id: int, flip_y: bool = True):
        from pyglet import gl
        if not getattr(self, '_fs_prog', None) or not getattr(self, '_fs_vbo', None):
            raise RuntimeError('Textured-quad resources not initialized')

        prog = int(self._fs_prog)
        prev_prog = gl.GLint()
        try:
            gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM, ctypes.byref(prev_prog))
        except Exception:
            prev_prog = None

        gl.glUseProgram(prog)

        # bind texture
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, int(tex_id))
        # set uniforms
        try:
            if self._fs_prog_u_tex is not None:
                gl.glUniform1i(self._fs_prog_u_tex, 0)
            if self._fs_prog_u_flip is not None:
                gl.glUniform1f(self._fs_prog_u_flip, 1.0 if flip_y else 0.0)
        except Exception:
            pass

        # If a VAO exists, bind it so attribute state is restored; otherwise set pointers directly
        bound_vao = False
        try:
            if getattr(self, '_fs_vao', None) is not None:
                try:
                    gl.glBindVertexArray(int(self._fs_vao))
                    bound_vao = True
                except Exception:
                    bound_vao = False
            else:
                gl.glBindBuffer(gl.GL_ARRAY_BUFFER, int(self._fs_vbo))
                stride = ctypes.sizeof(ctypes.c_float) * 4
                try:
                    gl.glEnableVertexAttribArray(self._fs_prog_attrib_pos)
                    gl.glVertexAttribPointer(self._fs_prog_attrib_pos, 2, gl.GL_FLOAT, False, stride, ctypes.c_void_p(0))
                    gl.glEnableVertexAttribArray(self._fs_prog_attrib_uv)
                    gl.glVertexAttribPointer(self._fs_prog_attrib_uv, 2, gl.GL_FLOAT, False, stride, ctypes.c_void_p(ctypes.sizeof(ctypes.c_float) * 2))
                except Exception:
                    pass
        except Exception:
            pass

        # blending for premultiplied alpha (Skia output)
        try:
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFuncSeparate(gl.GL_ONE, gl.GL_ONE_MINUS_SRC_ALPHA, gl.GL_ONE, gl.GL_ONE_MINUS_SRC_ALPHA)
        except Exception:
            pass

        try:
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        except Exception:
            try:
                err = int(gl.glGetError())
                logging.getLogger(__name__).debug('VBO glDrawArrays raised, glGetError=%r', err)
            except Exception:
                pass
            raise

        # Check GL error post-draw
        try:
            err = int(gl.glGetError())
            if err != 0:
                logging.getLogger(__name__).debug('VBO glDrawArrays completed but glGetError=%r', err)
        except Exception:
            pass

        # cleanup state
        try:
            if bound_vao:
                try:
                    gl.glBindVertexArray(0)
                except Exception:
                    pass
            else:
                try:
                    gl.glDisableVertexAttribArray(self._fs_prog_attrib_pos)
                    gl.glDisableVertexAttribArray(self._fs_prog_attrib_uv)
                except Exception:
                    pass
                try:
                    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        except Exception:
            pass
        try:
            if prev_prog is not None:
                gl.glUseProgram(int(prev_prog))
            else:
                gl.glUseProgram(0)
        except Exception:
            pass

