#!/usr/bin/env python3
"""
Test: draw with Skia (GPU when possible), show result in a pyglet window and save a PNG.

How it works:
- Creates a pyglet window (so we have an OpenGL context).
- Tries to create a Skia GPU context (GrDirectContext) bound to the current GL context,
  then makes a Skia GPU surface backed by an offscreen GL texture / FBO.
- Draws a simple scene (background + rectangle + stroked outline + crosshair).
- Snapshots the Skia surface to PNG bytes (via makeImageSnapshot().encodeToData()).
- Loads PNG bytes into pyglet.image and displays in the window.
- Writes PNG bytes to disk as 'skia_gpu_out.png'.

Notes / caveats:
- This code depends on the exact skia-python and pyglet versions / platform GL drivers.
  The GPU path may fail on some macOS installs or where skia-python wasn't built with GL.
- If GPU path fails it falls back to a CPU Skia Surface. If that also fails, there's a
  minimal Pillow fallback to create an image from the intended shapes.
"""
import io
import sys
import traceback

# prefer these imports at top for clarity
try:
    import skia
except Exception:
    skia = None

import pyglet
from pyglet import gl
import math

OUT_PNG = "skia_gpu_out.png"
WIDTH, HEIGHT = 640, 480


def draw_on_skia_surface(surface: "skia.Surface"):
    """Draw a simple test scene into a skia Surface's canvas."""
    canvas = surface.getCanvas()
    # Clear background to yellow
    canvas.clear(skia.Color4f(1.0, 1.0, 0.0, 1.0))
    # draw a green filled rectangle with blue stroke
    rect_paint = skia.Paint(
        Color=skia.Color4f(0.0, 1.0, 0.0, 1.0),
        isAntiAlias=True,
    )
    # Note: polar usage of Paint style; use two paints for fill and stroke
    rect = skia.Rect.MakeXYWH(160, 90, 320, 300)
    canvas.drawRect(rect, rect_paint)

    stroke_paint = skia.Paint(
        Color=skia.Color4f(0.0, 0.0, 1.0, 1.0),
        isAntiAlias=True,
        strokeWidth=6.0,
        stroke=True,
        style=skia.Paint.kStroke_Style,
    )
    canvas.drawRect(rect, stroke_paint)

    # crosshair at center
    cx = 160 + 320 / 2.0
    cy = 90 + 300 / 2.0
    cross_paint = skia.Paint(
        Color=skia.Color4f(1.0, 0.0, 1.0, 1.0), strokeWidth=2.0, isAntiAlias=True, stroke=True, style=skia.Paint.kStroke_Style
    )
    canvas.drawLine(cx - 12, cy, cx + 12, cy, cross_paint)
    canvas.drawLine(cx, cy - 12, cx, cy + 12, cross_paint)


def skia_gpu_render_to_png_bytes(width, height):
    """Attempt to render using Skia GPU surface and return PNG bytes."""
    if skia is None:
        raise RuntimeError("skia-python is not available")

    # Create GrDirectContext bound to current GL context
    # The skia-python API exposes GrDirectContext.MakeGL()
    ctx = skia.GrDirectContext.MakeGL()
    if ctx is None:
        raise RuntimeError("Failed to create GrDirectContext (MakeGL returned None)")

    # Create an offscreen GL texture and attach to framebuffer
    tex = gl.GLuint()
    gl.glGenTextures(1, gl.byref(tex))
    tex_id = int(tex.value)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
    # allocate texture storage (RGBA8)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
    # reasonable params
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    # Create a framebuffer and attach the texture (offscreen FBO)
    fbo = gl.GLuint()
    gl.glGenFramebuffers(1, gl.byref(fbo))
    fbo_id = int(fbo.value)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo_id)
    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, tex_id, 0)
    status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
    if status != gl.GL_FRAMEBUFFER_COMPLETE:
        # cleanup and raise
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        raise RuntimeError(f"Framebuffer not complete: status={status}")

    # Build GrGLFramebufferInfo and GrBackendRenderTarget for Skia
    # The skia.GrGLFramebufferInfo expects (fboid, format)
    # format is GL_RGBA8 (internal format). The exact constant may vary; skia expects an int.
    fb_info = skia.GrGLFramebufferInfo(fbo_id, int(gl.GL_RGBA8))
    backend_rt = skia.GrBackendRenderTarget(width, height, 0, 0, fb_info)

    # Make Skia Surface from backend render target.
    # origin: kBottomLeft_GrSurfaceOrigin (most GL contexts)
    surf = skia.Surface.MakeFromBackendRenderTarget(
        ctx,
        backend_rt,
        skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType,
        skia.ColorSpace.MakeSRGB(),
    )
    if surf is None:
        # cleanup GL objects
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        raise RuntimeError("Failed to create Skia GPU surface from backend target")

    # Draw on Skia surface
    draw_on_skia_surface(surf)

    # flush & submit to GPU
    ctx.flush()

    # Snapshot and encode PNG
    img = surf.makeImageSnapshot()
    data = img.encodeToData()
    png_bytes = data.tobytes()

    # cleanup GL binding to avoid interfering with pyglet window
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    # Note: we didn't delete texture/fbo here; the GL driver will free when context dies.
    return png_bytes


def skia_cpu_render_to_png_bytes(width, height):
    """Create a CPU Skia surface and return PNG bytes (fallback path)."""
    if skia is None:
        raise RuntimeError("skia-python is not available")

    info = skia.ImageInfo.Make(width, height, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kOpaque_AlphaType, skia.ColorSpace.MakeSRGB())
    surf = skia.Surface.MakeRaster(info)
    if surf is None:
        raise RuntimeError("Failed to create Skia CPU raster surface")

    draw_on_skia_surface(surf)
    img = surf.makeImageSnapshot()
    data = img.encodeToData()  # default PNG encoding
    return data.tobytes()


def pillow_fallback_png_bytes(width, height):
    """Minimal Pillow fallback to produce a PNG bytes of roughly the same scene."""
    try:
        from PIL import Image, ImageDraw
    except Exception:
        raise RuntimeError("Pillow not installed for fallback")

    img = Image.new("RGBA", (width, height), (255, 255, 0, 255))
    draw = ImageDraw.Draw(img)
    # green filled rectangle with blue outline
    rect = (160, 90, 160 + 320, 90 + 300)
    draw.rectangle(rect, fill=(0, 255, 0, 255), outline=(0, 0, 255, 255), width=6)
    # magenta cross
    cx = 160 + 320 // 2
    cy = 90 + 300 // 2
    draw.line((cx - 12, cy, cx + 12, cy), fill=(255, 0, 255, 255), width=2)
    draw.line((cx, cy - 12, cx, cy + 12), fill=(255, 0, 255, 255), width=2)

    bio = io.BytesIO()
    img.save(bio, "PNG")
    return bio.getvalue()


def get_png_bytes(width, height):
    """Try GPU path, then CPU skia path, then Pillow fallback."""
    excs = []
    if skia is not None:
        try:
            print("Attempting Skia GPU path...")
            return skia_gpu_render_to_png_bytes(width, height)
        except Exception as e:
            excs.append(("skia_gpu", e, traceback.format_exc()))
            print("Skia GPU path failed:", e)
        try:
            print("Attempting Skia CPU raster path...")
            return skia_cpu_render_to_png_bytes(width, height)
        except Exception as e:
            excs.append(("skia_cpu", e, traceback.format_exc()))
            print("Skia CPU raster path failed:", e)

    try:
        print("Falling back to Pillow raster path...")
        return pillow_fallback_png_bytes(width, height)
    except Exception as e:
        excs.append(("pillow", e, traceback.format_exc()))
        print("Pillow fallback failed:", e)

    # If all paths failed, raise a combined error
    msg = "All render paths failed. Details:\n"
    for name, err, tb in excs:
        msg += f"--- {name}: {err}\n{tb}\n"
    raise RuntimeError(msg)


def main():
    window = pyglet.window.Window(width=WIDTH, height=HEIGHT, caption="Skia->Pyglet test")

    # Produce PNG bytes from Skia / fallback
    png_bytes = None
    try:
        png_bytes = get_png_bytes(WIDTH, HEIGHT)
    except Exception as e:
        print("Failed to render image:", e)
        sys.exit(1)

    # Save to disk
    with open(OUT_PNG, "wb") as f:
        f.write(png_bytes)
    print("Wrote", OUT_PNG)

    # Load into pyglet image
    bio = io.BytesIO(png_bytes)
    try:
        pyg_img = pyglet.image.load(None, file=bio)
    except Exception as e:
        print("Failed to load PNG bytes into pyglet image:", e)
        pyg_img = None

    @window.event
    def on_draw():
        window.clear()
        if pyg_img is not None:
            # draw at 0,0 (pyglet origin is bottom-left)
            pyg_img.blit(0, 0)
        else:
            # nothing to draw
            pass

    print("Opening window. Close it to exit.")
    pyglet.app.run()


if __name__ == "__main__":
    main()