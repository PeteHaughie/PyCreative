"""Presenter adapter: manage a GL texture+FBO and a Skia Surface bound to it.

This adapter attempts to create a GPU-backed Skia surface (GrDirectContext +
backend render target) when an OpenGL context is available. If the GPU path
is not available it falls back to a CPU raster Skia Surface so callers still
receive a usable surface for headless rendering and testing.
"""
from __future__ import annotations

import ctypes
from typing import Optional, Any, Sequence


class SkiaGLPresenter:
    def __init__(self, width: int, height: int):
        self.width = int(width)
        self.height = int(height)
        self.tex_id: Optional[int] = None
        self.fbo_id: Optional[int] = None
        self.gr_context = None
        self.surface = None

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
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

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
            # Create GrDirectContext bound to current GL context
            ctx = skia.GrDirectContext.MakeGL()
            if ctx is None:
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
                return None

            self.gr_context = ctx
            self.surface = surf
            return surf
        except Exception:
            return None

    def render_commands(self, commands: Sequence[dict], replay_fn) -> Any:
        """Render a recorded command list into the GPU-backed Skia surface.

        This presenter is GPU-only: `create_skia_surface()` must return a
        valid GPU surface. If surface creation fails this function raises.
        """
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
            raise RuntimeError('Skia surface does not provide a canvas')

        # Do not clear the canvas here. The replay function is responsible
        # for applying any background command. Leaving the FBO contents
        # intact when no background is provided implements the Processing
        # semantics where drawings persist across frames unless explicitly
        # cleared by `background()`.

        # Call the replay function provided by the engine to draw recorded ops
        replay_fn(commands, canvas)

        # Flush/submit
        try:
            surf.flush()
        except Exception:
            pass

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
            # diagnostic logs removed for normal operation

            # Bind default framebuffer
            try:
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            except Exception as e:
                print('[DEBUG] present: glBindFramebuffer raised', repr(e))
            try:
                err = int(gl.glGetError())
                if err != 0:
                    print('[DEBUG] present: glGetError after glBindFramebuffer', err)
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
                        gl.glBlitFramebuffer(0, 0, int(self.width), int(self.height), 0, 0, int(vw), int(vh), gl.GL_COLOR_BUFFER_BIT, gl.GL_NEAREST)
                        blit_done = True
                    except Exception as e:
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
                    # Fall back to textured-quad immediate-mode drawing.
                    used_tex = False
                    try:
                        # Try binding the texture for use. If binding fails (e.g.,
                        # GL_TEXTURE_2D is not supported in this profile) we'll
                        # skip unbind/disable later.
                        try:
                            gl.glBindTexture(gl.GL_TEXTURE_2D, int(self.tex_id))
                            used_tex = True
                        except Exception as e:
                            pass
                    except Exception:
                        used_tex = False

                    try:
                        gl.glBegin(gl.GL_QUADS)
                    except Exception as e:
                            pass
                    try:
                        err = int(gl.glGetError())
                        if err != 0:
                            pass
                    except Exception:
                        pass
                    try:
                        gl.glTexCoord2f(0.0, 0.0); gl.glVertex2f(0.0, 0.0)
                        gl.glTexCoord2f(1.0, 0.0); gl.glVertex2f(float(vw), 0.0)
                        gl.glTexCoord2f(1.0, 1.0); gl.glVertex2f(float(vw), float(vh))
                        gl.glTexCoord2f(0.0, 1.0); gl.glVertex2f(0.0, float(vh))
                    except Exception as e:
                        pass
                    try:
                        gl.glEnd()
                    except Exception as e:
                        pass
                    try:
                        err = int(gl.glGetError())
                        if err != 0:
                            pass
                    except Exception:
                        pass
                    # Only unbind/disable if we successfully bound earlier
                    if used_tex:
                        try:
                            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
                        except Exception:
                            pass
                        try:
                            gl.glDisable(gl.GL_TEXTURE_2D)
                        except Exception:
                            pass
            except Exception:
                import traceback
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
        import skia
        # Find the last background command. If present, clear the canvas to
        # that color. If absent, do not clear so the FBO retains previous
        # frame contents (this is the Processing semantics for no-background
        # persistent drawing).
        bg_cmd = None
        for cmd in commands:
            if cmd.get('op') == 'background':
                bg_cmd = cmd
        if bg_cmd:
            r = bg_cmd['args'].get('r', 255)
            g = bg_cmd['args'].get('g', 255)
            b = bg_cmd['args'].get('b', 255)
            try:
                canvas.clear(skia.ColorSetRGB(r, g, b))
            except Exception:
                try:
                    canvas.clear(skia.Color4f(r / 255.0, g / 255.0, b / 255.0, 1.0))
                except Exception:
                    pass
        # If bg_cmd is None: do not clear; leave previous contents in the FBO so
        # shapes accumulate across frames unless the sketch explicitly clears.

        fill = (0, 0, 0)
        stroke = (0, 0, 0)
        stroke_weight = 1

        def _make_paint(color=None, style=skia.Paint.kFill_Style, width=1):
            p = skia.Paint()
            try:
                p.setAntiAlias(True)
            except Exception:
                pass
            if color is not None:
                try:
                    p.setColor(skia.ColorSetRGB(int(color[0]), int(color[1]), int(color[2])))
                except Exception:
                    try:
                        p.setColor(skia.Color4f(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0, 1.0))
                    except Exception:
                        pass
            try:
                p.setStyle(style)
            except Exception:
                pass
            if style == skia.Paint.kStroke_Style:
                try:
                    p.setStrokeWidth(float(width))
                except Exception:
                    pass
            return p

        for cmd in commands:
            op = cmd.get('op')
            args = cmd.get('args', {})

            if op == 'fill':
                fill = tuple(int(x) for x in args.get('color', fill))

            elif op == 'stroke':
                stroke = tuple(int(x) for x in args.get('color', stroke))

            elif op == 'stroke_weight':
                stroke_weight = int(args.get('weight', args.get('w', stroke_weight)))

            elif op == 'rect':
                x = float(args.get('x', 0))
                y = float(args.get('y', 0))
                w = float(args.get('w', 0))
                h = float(args.get('h', 0))
                # Per-shape override falls back to current drawing state
                local_fill = args.get('fill', fill)
                local_stroke = args.get('stroke', stroke)
                local_sw = int(args.get('stroke_weight', args.get('strokeWeight', args.get('w', stroke_weight))))
                if local_fill is not None:
                    paint = _make_paint(local_fill, style=skia.Paint.kFill_Style)
                    try:
                        canvas.drawRect(skia.Rect(x, y, x + w, y + h), paint)
                    except Exception:
                        pass
                if local_stroke is not None and local_sw > 0:
                    paint = _make_paint(local_stroke, style=skia.Paint.kStroke_Style, width=local_sw)
                    try:
                        canvas.drawRect(skia.Rect(x, y, x + w, y + h), paint)
                    except Exception:
                        pass

            elif op == 'line':
                x1 = float(args.get('x1', args.get('x', 0)))
                y1 = float(args.get('y1', args.get('y', 0)))
                x2 = float(args.get('x2', args.get('xend', 0)))
                y2 = float(args.get('y2', args.get('yend', 0)))
                local_stroke = args.get('stroke', stroke)
                local_sw = int(args.get('stroke_weight', args.get('strokeWeight', args.get('w', stroke_weight))))
                use_color = local_stroke if local_stroke is not None else (fill or (0, 0, 0))
                paint = _make_paint(use_color, style=skia.Paint.kStroke_Style, width=local_sw)
                try:
                    canvas.drawLine(x1, y1, x2, y2, paint)
                except Exception:
                    pass

            elif op == 'circle':
                # circle recorded as x,y,r
                cx = float(args.get('x', 0))
                cy = float(args.get('y', 0))
                r = float(args.get('r', 0))
                local_fill = args.get('fill', fill)
                local_stroke = args.get('stroke', stroke)
                local_sw = int(args.get('stroke_weight', args.get('strokeWeight', args.get('w', stroke_weight))))
                if local_fill is not None:
                    paint = _make_paint(local_fill, style=skia.Paint.kFill_Style)
                    try:
                        canvas.drawCircle(cx, cy, r, paint)
                    except Exception:
                        pass
                if local_stroke is not None and local_sw > 0:
                    paint = _make_paint(local_stroke, style=skia.Paint.kStroke_Style, width=local_sw)
                    try:
                        canvas.drawCircle(cx, cy, r, paint)
                    except Exception:
                        pass

    def teardown(self):
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

