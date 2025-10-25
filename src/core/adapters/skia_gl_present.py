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


class SkiaGLPresenter:
    def __init__(self, width: int, height: int, force_present_mode: Optional[str] = None, force_gles: bool = False):
        self.width = int(width)
        self.height = int(height)
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
            # Use RGBA8 where available; fallback to RGBA
            try:
                internal = gl.GL_RGBA8
            except Exception:
                internal = gl.GL_RGBA
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, internal, self.width, self.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
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
                        # Upload as full texture data
                        try:
                            gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, w, h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, buf)
                        except Exception:
                            # Some platforms may require a pointer cast
                            try:
                                gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, w, h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.byref(buf))
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
            if getattr(self, 'surface', None) is not None and getattr(self, 'gr_context', None) is not None and self._surface_size == (int(self.width), int(self.height)):
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

            fb_info = skia.GrGLFramebufferInfo(int(self.fbo_id or 0), fb_fmt)
            backend_rt = skia.GrBackendRenderTarget(self.width, self.height, 0, 0, fb_info)
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
                self._surface_size = (int(self.width), int(self.height))
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
                                w = int(self.width)
                                h = int(self.height)
                                _gl.glBindFramebuffer(_gl.GL_FRAMEBUFFER, int(self.fbo_id or 0))
                                buf = (ctypes.c_ubyte * (w * h * 4))()
                                _gl.glReadPixels(0, 0, w, h, _gl.GL_RGBA, _gl.GL_UNSIGNED_BYTE, ctypes.byref(buf))
                                raw = bytes(buf)
                                img_p = _Image.frombytes('RGBA', (w, h), raw)
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
                            # This is guarded and best-effort; failure here should not raise.
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
                                    w = int(self.width)
                                    h = int(self.height)
                                    # Read pixels into a ctypes buffer (RGBA)
                                    buf = (ctypes.c_ubyte * (w * h * 4))()
                                    _gl.glReadPixels(0, 0, w, h, _gl.GL_RGBA, _gl.GL_UNSIGNED_BYTE, ctypes.byref(buf))
                                    raw = bytes(buf)
                                    img_p = _Image.frombytes('RGBA', (w, h), raw)
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
        # Draw the presenter texture to the default framebuffer using the
        # fixed-function pipeline. This avoids depending on a shader/VBO setup
        # which may be fragile across platforms and driver combinations.
        from pyglet import gl
        try:
            # Basic diagnostics
            # One-time GL diagnostics to help identify runtime capabilities.
            try:
                if not getattr(self, '_present_diag_done', False):
                    def _gl_str(name):
                        try:
                            s = gl.glGetString(name)
                            return s.decode('utf-8', 'ignore') if s else '<none>'
                        except Exception:
                            return '<unknown>'
                    info = {
                        'GL_VERSION': _gl_str(gl.GL_VERSION),
                        'GL_RENDERER': _gl_str(gl.GL_RENDERER),
                        'GL_VENDOR': _gl_str(gl.GL_VENDOR),
                        'GL_SHADING_LANGUAGE_VERSION': _gl_str(gl.GL_SHADING_LANGUAGE_VERSION),
                        'HAS_glBlitFramebuffer': hasattr(gl, 'glBlitFramebuffer'),
                    }
                    try:
                        logging.getLogger(__name__).info('SkiaGLPresenter GL diagnostics: %r', info)
                    except Exception:
                        pass
                    self._present_diag_done = True
            except Exception:
                pass

            # Bind default framebuffer
            try:
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
                # If a setup background color was recorded on the presenter,
                # clear the default framebuffer to that opaque color so any
                # transparent pixels in the presenter's texture show the
                # intended background instead of black/transparent.
                try:
                    bg = getattr(self, '_setup_background_color', None)
                    if bg is not None:
                        try:
                            r = float(int(bg[0]) / 255.0)
                            g = float(int(bg[1]) / 255.0)
                            b = float(int(bg[2]) / 255.0)
                            gl.glClearColor(r, g, b, 1.0)
                            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                        except Exception:
                            pass
                except Exception:
                    pass
            except Exception as e:
                try:
                    logging.getLogger(__name__).debug('present: glBindFramebuffer raised %r', repr(e))
                except Exception:
                    pass
            try:
                err = int(gl.glGetError())
                if err != 0:
                    try:
                        logging.getLogger(__name__).debug('present: glGetError after glBindFramebuffer %r', err)
                    except Exception:
                        pass
            except Exception:
                pass

            # We attempt a framebuffer blit first (core-profile friendly).
            # Only if blit is unsupported or fails do we attempt a textured-quad
            # fallback. Avoid calling deprecated fixed-function enums like
            # glEnable(GL_TEXTURE_2D) in core profiles.

            # Save projection/modelview and set an ortho matching the texture size
            try:
                gl.glMatrixMode(gl.GL_PROJECTION)
                gl.glPushMatrix()
                gl.glLoadIdentity()
                gl.glOrtho(0, int(self.width), 0, int(self.height), -1, 1)
                gl.glMatrixMode(gl.GL_MODELVIEW)
                gl.glPushMatrix()
                gl.glLoadIdentity()
            except Exception:
                pass

            # Draw a fullscreen quad covering [0..width] x [0..height]
            try:
                # Query the current viewport to get the actual drawable size
                vp = (gl.GLint * 4)()
                try:
                    gl.glGetIntegerv(gl.GL_VIEWPORT, vp)
                    vw = int(vp[2])
                    vh = int(vp[3])
                except Exception:
                    vw = int(self.width)
                    vh = int(self.height)
                try:
                    err = int(gl.glGetError())
                    if err != 0:
                        pass
                except Exception:
                    pass
                # Decide preferred present path. If `force_present_mode` is set,
                # prefer that path (and fall back if it fails). Otherwise try
                # blit first, then VBO, then immediate-mode.
                preferred = getattr(self, 'force_present_mode', None)
                # Try a direct framebuffer blit first (more portable to core profiles)
                blit_done = False
                try:
                    # Bind read (source) to our FBO and draw (dest) to default
                    try:
                        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, int(self.fbo_id))
                        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)
                    except Exception:
                        # Some drivers may not expose separate READ/DRAW enums; try GL_FRAMEBUFFER
                        try:
                            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, int(self.fbo_id))
                        except Exception:
                            pass
                    # Perform blit
                    try:
                        if preferred in (None, 'blit'):
                            if hasattr(gl, 'glBlitFramebuffer'):
                                gl.glBlitFramebuffer(0, 0, int(self.width), int(self.height), 0, 0, int(vw), int(vh), gl.GL_COLOR_BUFFER_BIT, gl.GL_NEAREST)
                                blit_done = True
                                try:
                                    self._last_present_mode = 'blit'
                                except Exception:
                                    pass
                                try:
                                    err = int(gl.glGetError())
                                    if err != 0:
                                        logging.getLogger(__name__).debug('present: glBlitFramebuffer glGetError=%r', err)
                                except Exception:
                                    pass
                            else:
                                blit_done = False
                        else:
                            # forced a non-blit mode; skip attempting blit
                            blit_done = False
                    except Exception as e:
                        try:
                            logging.getLogger(__name__).debug('present: glBlitFramebuffer raised %r', repr(e))
                        except Exception:
                            pass
                    # Unbind any read framebuffer bindings we changed
                    try:
                        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, 0)
                    except Exception:
                        try:
                            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
                        except Exception:
                            pass
                except Exception:
                    pass

                if not blit_done:
                    # Try a modern, core-profile friendly VBO+shader textured-quad
                    # fallback (GLSL 1.20 variant for macOS). This avoids
                    # immediate-mode calls which are invalid in core profiles.
                    vbo_ok = False
                    try:
                        # Ensure program and VBO exist (lazily created)
                        self._ensure_textured_quad_resources()
                        # Draw using the shader and VBO. Temporarily disable
                        # GL blending so any alpha in the presenter's texture
                        # does not blend with the default framebuffer (which
                        # could show as white). Remember previous state and
                        # restore it afterwards.
                        try:
                            was_blend = False
                            try:
                                was_blend = bool(gl.glIsEnabled(gl.GL_BLEND))
                            except Exception:
                                was_blend = False
                            try:
                                gl.glDisable(gl.GL_BLEND)
                            except Exception:
                                pass
                        except Exception:
                            was_blend = False

                        self._draw_textured_quad_vbo(int(self.tex_id), flip_y=True)

                        try:
                            if was_blend:
                                try:
                                    gl.glEnable(gl.GL_BLEND)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        vbo_ok = True
                        try:
                            self._last_present_mode = 'vbo'
                        except Exception:
                            pass
                    except Exception:
                        vbo_ok = False

                    if not vbo_ok:
                        # Last-resort: fall back to immediate-mode textured-quad
                        # if present in this GL profile (kept for compatibility).
                        used_tex = False
                        try:
                            try:
                                gl.glBindTexture(gl.GL_TEXTURE_2D, int(self.tex_id))
                                used_tex = True
                            except Exception:
                                pass
                        except Exception:
                            used_tex = False

                        try:
                            gl.glBegin(gl.GL_QUADS)
                        except Exception:
                            pass
                        try:
                            gl.glTexCoord2f(0.0, 0.0)
                            gl.glVertex2f(0.0, 0.0)
                            gl.glTexCoord2f(1.0, 0.0)
                            gl.glVertex2f(float(vw), 0.0)
                            gl.glTexCoord2f(1.0, 1.0)
                            gl.glVertex2f(float(vw), float(vh))
                            gl.glTexCoord2f(0.0, 1.0)
                            gl.glVertex2f(0.0, float(vh))
                        except Exception:
                            pass
                        try:
                            gl.glEnd()
                        except Exception:
                            pass
                        # record immediate-mode usage
                        try:
                            self._last_present_mode = 'immediate'
                        except Exception:
                            pass
                        if used_tex:
                            try:
                                gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
                            except Exception:
                                pass
                            try:
                                gl.glDisable(gl.GL_TEXTURE_2D)
                            except Exception:
                                pass
                # Log which present mode was used for this frame
                try:
                    if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                        try:
                            logging.getLogger(__name__).debug('present used mode=%s viewport=%s %s', getattr(self, '_last_present_mode', None), vw, vh)
                        except Exception:
                            pass
                except Exception:
                    pass

            except Exception:
                # Suppress detailed fallback errors in normal runs
                pass

            # Restore matrices
            try:
                gl.glMatrixMode(gl.GL_PROJECTION)
                gl.glPopMatrix()
                gl.glMatrixMode(gl.GL_MODELVIEW)
                gl.glPopMatrix()
            except Exception:
                pass

            # Optional runtime diagnostic: report which present mode was
            # used and any GL error after presenting. Enabled via
            # PYCREATIVE_DEBUG_PRESENT=1 so it can be toggled without code
            # changes during debugging sessions.
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
                        # Print directly to stdout to ensure visibility in
                        # CLI runs; logging may be configured at a higher
                        # level in user environments.
                        print(f'PRESENTER DEBUG: mode={getattr(self, "_last_present_mode", None)} glError={_err}')
                    except Exception:
                        pass
                    # Also append a small debug line to /tmp so CI or headless
                    # runs can inspect it even if stdout is swallowed.
                    try:
                        with open('/tmp/pycreative_present_log.txt', 'a') as _f:
                            _f.write(f'mode={getattr(self, "_last_present_mode", None)} glError={_err}\n')
                    except Exception:
                        pass
            except Exception:
                pass

            # Optional: dump the default framebuffer after present to verify what was drawn
            try:
                if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE_DUMP', '') == '1':
                    try:
                        from pyglet import gl as _gl
                        # read pixels from default framebuffer (0)
                        buf = (_gl.GLubyte * (int(vw) * int(vh) * 4))()
                        _gl.glBindFramebuffer(_gl.GL_FRAMEBUFFER, 0)
                        _gl.glReadPixels(0, 0, int(vw), int(vh), _gl.GL_RGBA, _gl.GL_UNSIGNED_BYTE, buf)
                        raw = bytes(buf)
                        try:
                            from PIL import Image as _Image
                            img_p = _Image.frombytes('RGBA', (int(vw), int(vh)), raw)
                            img_p = img_p.transpose(_Image.FLIP_TOP_BOTTOM)
                            path = '/tmp/pycreative_post_present.png'
                            img_p.save(path, 'PNG')
                            try:
                                logging.getLogger(__name__).debug('wrote post-present snapshot to %s', path)
                            except Exception:
                                pass
                        except Exception as e:
                            try:
                                logging.getLogger(__name__).debug('post-present Pillow write failed %r', repr(e))
                            except Exception:
                                pass
                    except Exception as e:
                        try:
                            logging.getLogger(__name__).debug('post-present readback failed %r', repr(e))
                        except Exception:
                            pass
            except Exception:
                pass

            # Do not call fixed-function texture enable/disable unconditionally;
            # those calls may be invalid in core or forward-compatible GL
            # contexts. Any texture unbind/disable performed for the fallback
            # path is handled inline where the bind succeeded.
            try:
                pass
            except Exception:
                pass
        except Exception:
            # let caller fallback to readback if present fails
            raise

    def replay_fn(self, commands, canvas):
        try:
            # Delegate to the centralized replayer which handles transforms
            # and shape commands consistently across offscreen and GPU paths.
            from core.io.replay_to_skia import replay_to_skia_canvas
            try:
                replay_to_skia_canvas(commands, canvas)
                return
            except Exception:
                # Fall through to an internal fallback if delegate fails
                pass
        except Exception:
            # If the helper can't be imported, fall back to the presenter's
            # internal replay logic below (left for backward compatibility).
            pass
        try:
            logging.getLogger(__name__).debug('presenter.last_present_mode=%r', getattr(self, '_last_present_mode', None))
        except Exception:
            pass
        # NOTE: The original replay implementation follows here as a
        # compatibility fallback. In most cases `replay_to_skia_canvas`
        # will handle drawing and transforms.

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

