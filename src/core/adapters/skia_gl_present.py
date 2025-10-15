"""Presenter adapter: manage a GL texture+FBO and a Skia Surface bound to it.

Provides methods to render Skia into the FBO and present it to the default
framebuffer. Falls back to readback if needed.
"""
from __future__ import annotations

import ctypes
from typing import Optional, Any


class SkiaGLPresenter:
    def __init__(self, width: int, height: int):
        self.width = int(width)
        self.height = int(height)
        self.tex_id: Optional[int] = None
        self.fbo_id: Optional[int] = None
        self.gr_context = None
        self.surface = None

    def ensure_resources(self):
        # Lazy import to avoid top-level pyglet dependency
        from pyglet import gl
        if self.tex_id is None:
            tex = gl.GLuint()
            gl.glGenTextures(1, ctypes.byref(tex))
            self.tex_id = int(tex.value)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex_id)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA8, self.width,
                            self.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        if self.fbo_id is None:
            f = gl.GLuint()
            gl.glGenFramebuffers(1, ctypes.byref(f))
            self.fbo_id = int(f.value)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo_id)
            gl.glFramebufferTexture2D(
                gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, int(self.tex_id), 0)
            status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
            if status != gl.GL_FRAMEBUFFER_COMPLETE:
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
                raise RuntimeError('FBO incomplete: %r' % (status,))
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def create_skia_surface(self):
        # Create GrDirectContext and Skia surface bound to the FBO
        try:
            import skia
        except Exception:
            raise
        if self.gr_context is None:
            self.gr_context = skia.GrDirectContext.MakeGL()
        if self.surface is None:
            fb_info = skia.GrGLFramebufferInfo(
                self.fbo_id, int(0x8058))  # GL_RGBA8
            backend = skia.GrBackendRenderTarget(
                self.width, self.height, 0, 0, fb_info)
            surf = skia.Surface.MakeFromBackendRenderTarget(
                self.gr_context, backend, skia.kBottomLeft_GrSurfaceOrigin, skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
            if surf is None:
                raise RuntimeError('Skia Surface creation failed')
            self.surface = surf
        return self.surface

    def render_commands(self, commands: list, replay_fn):
        """Render recorded commands using the provided replay_fn(canvas, commands)

        `replay_fn` should accept (commands, canvas) and draw into the canvas.
        """
        from pyglet import gl
        self.ensure_resources()
        surf = self.create_skia_surface()
        canvas = surf.getCanvas()
        # clear before replay
        try:
            canvas.clear(skia.Color4f(1, 1, 1, 1))
        except Exception:
            try:
                canvas.clear(0xFFFFFFFF)
            except Exception:
                pass
        # Replay
        replay_fn(commands, canvas)
        # flush and submit
        try:
            surf.flush()
        except Exception:
            pass
        try:
            if hasattr(self.gr_context, 'flush'):
                self.gr_context.flush()
            if hasattr(self.gr_context, 'submit'):
                self.gr_context.submit()
        except Exception:
            pass
        from pyglet import gl as _gl
        try:
            _gl.glFlush()
            _gl.glFinish()
        except Exception:
            pass

    def present(self):
        # Modern OpenGL: draw textured quad using shaders and vertex buffers
        # This is a placeholder. You should implement a VAO/VBO and shader program to draw the texture.
        # For now, you can use pyglet's built-in texture blit if available, or integrate with pyglet.graphics.
        from pyglet import gl
        try:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, int(self.tex_id))
            # TODO: Implement shader-based textured quad rendering here.
            # See pyglet.graphics or pyglet.sprite for reference implementations.
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        except Exception:
            # let caller fallback to readback if present fails
            raise
    
    def replay_fn(self, commands, canvas):
        import skia
        """
        # Draw a blue rectangle for testing
        paint = skia.Paint(Color=skia.ColorBLUE,
                           Style=skia.Paint.kFill_Style, AntiAlias=True)
        canvas.drawRect(skia.Rect(50, 50, 200, 200), paint)
        """

        # fill = skia.Paint(Color=skia.ColorSetRGB(0, 0, 0))
        # print('REPLAY_FN', commands)

        # Find the last background command
        bg_cmd = None
        for cmd in commands:
            if cmd['op'] == 'background':
                print('FOUND BG CMD', cmd)
                bg_cmd = cmd
        if bg_cmd:
            r = bg_cmd['args'].get('r', 255)
            g = bg_cmd['args'].get('g', 255)
            b = bg_cmd['args'].get('b', 255)
            canvas.clear(skia.ColorSetRGB(r, g, b))
        else:
            canvas.clear(skia.ColorSetRGB(200, 200, 200))  # default gray

        fill = (0, 0, 0)
        stroke = (0, 0, 0)
        stroke_weight = 1

        for cmd in commands:
            if cmd['op'] == 'fill':
                args = cmd['args']
                fill = args.get('color', (0, 0, 0))
                paint = skia.Paint(
                    Color=skia.ColorSetRGB(*fill),
                    Style=skia.Paint.kFill_Style,
                    AntiAlias=True
                )
            if cmd['op'] == 'background':
                print('BG CMD', cmd)
                args = cmd['args']
                bg = args.get('color', (255, 255, 255))
                canvas.clear(skia.ColorSetRGB(*bg))
                print('FILL', cmd.get('fill_r', 0), cmd.get('fill_g', 0), cmd.get('fill_b', 0))
                r = bg_cmd['args'].get('r', 255)
                g = bg_cmd['args'].get('g', 255)
                b = bg_cmd['args'].get('b', 255)
                # if cmd['op'] == 'ellipse':
                canvas.clear(skia.ColorSetRGB(r, g, b))
        #         paint = skia.Paint(
        #             Color=skia.ColorSetRGB(cmd.get('fill_r', 0), cmd.get('fill_g', 0), cmd.get('fill_b', 0)),
        #             Style=skia.Paint.kFill_Style,
        #             AntiAlias=True
        #         )
        #         canvas.drawOval(
        #             skia.Rect(cmd["x"], cmd["y"], cmd["x"] + cmd["w"], cmd["y"] + cmd["h"]), paint)
            if cmd['op'] == 'rect':
                args = cmd['args']
                x, y, w, h = args['x'], args['y'], args['w'], args['h']
                # fill = args.get('fill', (255, 255, 255))
                paint = skia.Paint(
                    Color=skia.ColorSetRGB(*fill),
                    Style=skia.Paint.kFill_Style,
                    AntiAlias=True
                )
                canvas.drawRect(skia.Rect(x, y, x + w, y + h), paint)

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
