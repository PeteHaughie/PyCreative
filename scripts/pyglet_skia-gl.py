import contextlib
import pyglet
import skia
import sys
from OpenGL import GL

WIDTH, HEIGHT = 640, 480
x = 0
window = pyglet.window.Window(WIDTH, HEIGHT, "Skia-Pyglet-GL")

@contextlib.contextmanager
def skia_surface(window):
    context = skia.GrDirectContext.MakeGL()
    (fb_width, fb_height) = window.get_framebuffer_size()
    backend_render_target = skia.GrBackendRenderTarget(
        fb_width,
        fb_height,
        0,  # sampleCnt
        0,  # stencilBits
        skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
    surface = skia.Surface.MakeFromBackendRenderTarget(
        context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
    assert surface is not None
    yield surface
    context.abandonContext()


@window.event
def on_draw():
    global x
    window.clear()
    with skia_surface(window) as surface:
        with surface as canvas:
            paint = skia.Paint(
                Color=skia.ColorBLUE,
                Style=skia.Paint.kFill_Style,
                AntiAlias=True
            )
            canvas.drawRect(skia.Rect(x, 100, 300, 300), paint)
        surface.flushAndSubmit()
    x = (x + 5) % WIDTH
pyglet.app.run()