#!/usr/bin/env python3
"""Zero-copy Skia->pyglet demo.

Attempt to create a GL texture, make a Skia GPU surface that draws into that
texture (via GrBackendTexture or backend render target), then display the same
texture directly in a pyglet window. This avoids an extra GPU->CPU roundtrip.

This is platform- and skia-python-version sensitive. It will attempt a
zero-copy backend-texture path first, and fall back to the FBO->snapshot->texture
approach if the first path is not supported.

Run with:
    python test-skia-pyglet-zero-copy.py

Requirements:
    - pyglet
    - skia-python (built with GL support for GPU path)

Caveats:
    - On macOS skia-python may not support GL-backed GPU contexts depending on
      how it was built. In that case the script will fall back to a safe
      snapshot-based rendering path.
"""
from __future__ import annotations

import io
import sys
import time
import traceback

try:
    import skia
except Exception:
    skia = None

print('[TRACE] module loaded', flush=True)

import pyglet
from pyglet import gl
from pyglet import shapes
import ctypes
import signal

WIDTH, HEIGHT = 640, 480
OUT = 'skia_zero_copy.png'

def create_gl_texture(w, h):
    print('[TRACE] create_gl_texture start', flush=True)
    tex = gl.GLuint()
    gl.glGenTextures(1, ctypes.byref(tex))
    tex_id = int(tex.value)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    # allocate storage
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    print('[TRACE] create_gl_texture done tex_id=', tex_id, flush=True)
    return tex_id


def draw_scene_to_skia_canvas(canvas: "skia.Canvas"):
    # simple scene
    # clear background (use Color4f if available)
    try:
        canvas.clear(skia.Color4f(1, 1, 0, 1))
    except Exception:
        try:
            canvas.clear(skia.ColorSetRGB(1.0, 1.0, 0.0))
        except Exception:
            # last resort: clear with integer color
            try:
                canvas.clear(0xFFFFFF00)
            except Exception:
                pass

    rect = skia.Rect.MakeXYWH(160, 90, 320, 300)

    def make_paint(r, g, b, a=1.0, stroke=False, stroke_width=1.0):
        p = skia.Paint()
        # anti-alias
        try:
            p.setAntiAlias(True)
        except Exception:
            try:
                p.set_isAntiAlias(True)
            except Exception:
                pass
        # set color: prefer Color4f, fall back to integer color
        try:
            col = skia.Color4f(r, g, b, a)
            p.setColor(col)
        except Exception:
            try:
                icol = (int(a * 255) << 24) | (int(r * 255) << 16) | (int(g * 255) << 8) | int(b * 255)
                p.setColor(icol)
            except Exception:
                pass
        # style
        try:
            if stroke:
                p.setStyle(skia.Paint.kStroke_Style)
                p.setStrokeWidth(float(stroke_width))
            else:
                p.setStyle(skia.Paint.kFill_Style)
        except Exception:
            # ignore style failures
            pass
        return p

    fill_p = make_paint(0.0, 1.0, 0.0, 1.0, stroke=False)
    canvas.drawRect(rect, fill_p)
    stroke_p = make_paint(0.0, 0.0, 1.0, 1.0, stroke=True, stroke_width=6.0)
    canvas.drawRect(rect, stroke_p)
    cx = 160 + 320/2.0
    cy = 90 + 300/2.0
    cross = make_paint(1.0, 0.0, 1.0, 1.0, stroke=True, stroke_width=2.0)
    canvas.drawLine(cx-12, cy, cx+12, cy, cross)
    canvas.drawLine(cx, cy-12, cx, cy+12, cross)


def zero_copy_skia_to_texture(w, h, tex_id):
    """Attempt to create a Skia surface that writes directly into `tex_id`.

    Returns True on success, False otherwise.
    """
    print('[TRACE] zero_copy_skia_to_texture start', flush=True)
    if skia is None:
        print('skia-python not available')
        return False
    try:
        print('[TRACE] calling GrDirectContext.MakeGL', flush=True)
        ctx = skia.GrDirectContext.MakeGL()
        if ctx is None:
            print('GrDirectContext.MakeGL returned None')
            return False

        # build GrBackendTexture description
        # Note: skia.GrBackendTexture.MakeGL assumes a Python int texture id and
        # uses the provided format. This API is version sensitive; adapt if
        # your skia-python has a different signature.
        # Construct GrMipMapped constant defensively as API names vary across skia-python builds
        try:
            mip = skia.GrMipMapped.kNo
        except Exception:
            try:
                mip = skia.GrMipmapped.kNo
            except Exception:
                mip = 0
        # Construct GrGLTextureInfo/GrBackendTexture in a version-tolerant way
        try:
                tex_info = skia.GrGLTextureInfo(int(tex_id), int(gl.GL_RGBA8))
                backend_tex = skia.GrBackendTexture(w, h, mip, tex_info)
        except Exception:
            # Some skia versions invert the arg order or names; try alternative signature
            try:
                tex_info = skia.GrGLTextureInfo(int(gl.GL_RGBA8), int(tex_id))
                backend_tex = skia.GrBackendTexture(w, h, mip, tex_info)
            except Exception:
                raise

        # Create surface from backend texture
        print('[TRACE] calling MakeFromBackendTexture', flush=True)
        surf = skia.Surface.MakeFromBackendTexture(ctx, backend_tex, skia.kTopLeft_GrSurfaceOrigin, skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB(), {})
        if surf is None:
            print('MakeFromBackendTexture returned None')
            return False
        print('[TRACE] drawing to skia surface canvas', flush=True)
        draw_scene_to_skia_canvas(surf.getCanvas())
        print('[TRACE] flushing context', flush=True)
        ctx.flush()
        return True
    except Exception as e:
        print('zero_copy path failed:', e)
        traceback.print_exc()
        return False


def zero_copy_backend_texture(w, h, tex_id):
    """Attempt true zero-copy by creating a GrBackendTexture from an existing GL texture id
    and making a Skia surface that draws directly into that backend texture.

    Returns (success: bool, ctx) where ctx is the GrDirectContext used (or None).
    """
    if skia is None:
        print('[ZERO] skia-python not available')
        return False, None

    print('[ZERO] zero_copy_backend_texture start (FBO attach method)', flush=True)
    if skia is None:
        print('[ZERO] skia-python not available', flush=True)
        return False, None
    try:
        print('[ZERO] calling GrDirectContext.MakeGL', flush=True)
        ctx = skia.GrDirectContext.MakeGL()
        print('[ZERO] GrDirectContext.MakeGL returned:', 'None' if ctx is None else 'ok', flush=True)
        if ctx is None:
            return False, None

        # Create a new framebuffer and attach the provided texture. This avoids
        # constructing GrBackendTexture which is known to block on some builds.
        fbo = gl.GLuint()
        gl.glGenFramebuffers(1, ctypes.byref(fbo))
        fbo_id = int(fbo.value)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo_id)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, int(tex_id), 0)
        status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            print('[ZERO] attached FBO incomplete, status=', status, flush=True)
            return False, ctx

        print('[ZERO] attached texture', tex_id, 'to fbo', fbo_id, flush=True)

        # Build a GrBackendRenderTarget pointing at the FBO (no new texture creation)
        fb_info = skia.GrGLFramebufferInfo(fbo_id, int(gl.GL_RGBA8))
        backend_rt = skia.GrBackendRenderTarget(w, h, 0, 0, fb_info)

        print('[ZERO] calling MakeFromBackendRenderTarget', flush=True)
        surf = skia.Surface.MakeFromBackendRenderTarget(ctx, backend_rt, skia.kBottomLeft_GrSurfaceOrigin, skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
        if surf is None:
            print('[ZERO] MakeFromBackendRenderTarget returned None', flush=True)
            try:
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            except Exception:
                pass
            return False, ctx

        print('[ZERO] drawing to backend texture via Skia (attached FBO)', flush=True)
        draw_scene_to_skia_canvas(surf.getCanvas())
        ctx.flush()
        print('[ZERO] ctx.flush done (attached FBO)', flush=True)

        # unbind the FBO but don't delete it immediately; let caller display the texture
        try:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        except Exception:
            pass
        return True, ctx

    except Exception as e:
        print('[ZERO] zero-copy backend exception (attached FBO):', e, flush=True)
        traceback.print_exc()
        try:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        except Exception:
            pass
        return False, None


def fbo_skia_render_and_snapshot(w, h):
    """Fallback: create a GL FBO, let Skia render into it via backend render target,
    snapshot to PNG bytes, and return bytes.
    """
    if skia is None:
        raise RuntimeError('skia-python required for fallback')
    print('[TRACE] fbo_skia_render_and_snapshot start', flush=True)
    # generate fbo and texture
    tex = gl.GLuint()
    print('[TRACE] glGenTextures start', flush=True)
    gl.glGenTextures(1, ctypes.byref(tex))
    tex_id = int(tex.value)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    fbo = gl.GLuint()
    gl.glGenFramebuffers(1, ctypes.byref(fbo))
    fbo_id = int(fbo.value)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo_id)
    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, tex_id, 0)
    status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
    if status != gl.GL_FRAMEBUFFER_COMPLETE:
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        raise RuntimeError('FBO incomplete')

    print('[TRACE] built FBO and texture, fb=', fbo_id, 'tex=', tex_id, flush=True)
    fb_info = skia.GrGLFramebufferInfo(fbo_id, int(gl.GL_RGBA8))
    backend_rt = skia.GrBackendRenderTarget(w, h, 0, 0, fb_info)
    print('[TRACE] calling GrDirectContext.MakeGL for FBO', flush=True)
    ctx = skia.GrDirectContext.MakeGL()
    print('[TRACE] calling MakeFromBackendRenderTarget', flush=True)
    surf = skia.Surface.MakeFromBackendRenderTarget(ctx, backend_rt, skia.kBottomLeft_GrSurfaceOrigin, skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
    if surf is None:
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        raise RuntimeError('MakeFromBackendRenderTarget failed')

    print('[TRACE] drawing to FBO Skia surface', flush=True)
    draw_scene_to_skia_canvas(surf.getCanvas())
    print('[TRACE] flushing FBO context', flush=True)
    ctx.flush()
    img = surf.makeImageSnapshot()
    data = None
    try:
        data = img.encodeToData()
    except Exception:
        data = None

    if data is not None:
        png_bytes = data.tobytes()
    else:
        # Fallback: read pixels from the FBO and encode via Pillow
        print('[TRACE] encodeToData returned None; falling back to glReadPixels + Pillow', flush=True)
        # Bind the FBO we used earlier
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo_id)
        buf = (gl.GLubyte * (w * h * 4))()
        gl.glReadPixels(0, 0, w, h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, buf)
        raw = bytes(buf)
        # Pillow expects rows top-to-bottom, GL gives bottom-to-top, so flip
        try:
            from PIL import Image
        except Exception:
            raise RuntimeError('Pillow required for FBO readback fallback')
        img_p = Image.frombytes('RGBA', (w, h), raw)
        img_p = img_p.transpose(Image.FLIP_TOP_BOTTOM)
        bio = io.BytesIO()
        img_p.save(bio, 'PNG')
        png_bytes = bio.getvalue()
        # unbind FBO
        try:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        except Exception:
            pass
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
    print('[TRACE] fbo snapshot complete, len=', len(png_bytes), flush=True)
    return png_bytes, tex_id


def main():
    import argparse

    print('[TRACE] main start', flush=True)

    parser = argparse.ArgumentParser(prog='test-skia-pyglet-zero-copy', description='Skia -> pyglet zero-copy demo (zero-copy is opt-in)')
    parser.add_argument('--zero-copy', action='store_true', help='Attempt zero-copy path (may hang on some platforms)')
    parser.add_argument('--zero-copy-timeout', type=float, default=5.0, help='Seconds to wait for zero-copy path before falling back (no effect unless --zero-copy is used)')
    args = parser.parse_args()

    print('[TRACE] creating pyglet window', flush=True)
    window = pyglet.window.Window(width=WIDTH, height=HEIGHT, caption='Skia zero-copy demo')
    print('[TRACE] pyglet window created', flush=True)

    # Ensure we can exit the pyglet event loop from signals (Ctrl-C) or window close
    def _exit_app(*_):
        try:
            pyglet.app.exit()
        except Exception:
            pass

    # handle Ctrl-C and termination
    try:
        signal.signal(signal.SIGINT, lambda *_: _exit_app())
        signal.signal(signal.SIGTERM, lambda *_: _exit_app())
    except Exception:
        # some environments may not allow signal handlers (e.g., embedded)
        pass

    # Robust exit handler to ensure clean shutdown
    def _exit_app(*_):
        try:
            if window and not window.has_exit:
                window.close()
        except Exception:
            pass
        try:
            pyglet.app.exit()
        except Exception:
            pass

    @window.event
    def on_close():
        _exit_app()
        return True

    # Also handle SIGINT and SIGTERM for clean exit
    import signal
    try:
        signal.signal(signal.SIGINT, lambda *_: _exit_app())
        signal.signal(signal.SIGTERM, lambda *_: _exit_app())
    except Exception:
        pass

    # safety: auto-exit after 15s so a headless CI won't hang indefinitely
    pyglet.clock.schedule_once(lambda dt: _exit_app(), 15.0)

    # create a GL texture to share
    print('[TRACE] calling create_gl_texture', flush=True)
    tex_id = create_gl_texture(WIDTH, HEIGHT)
    print('[TRACE] created texture id', tex_id, flush=True)

    zero_ok = False
    if args.zero_copy:
        print('User requested zero-copy; attempting with timeout', args.zero_copy_timeout)
        # run zero-copy attempt but don't let it hang the process: try/catch and let it raise if it fails
        try:
            # prefer backend-texture zero-copy (true zero-copy) first
            zero_ok, ctx = zero_copy_backend_texture(WIDTH, HEIGHT, tex_id)
            if not zero_ok:
                # fall back to previous approach
                zero_ok = zero_copy_skia_to_texture(WIDTH, HEIGHT, tex_id)
        except Exception as e:
            print('Zero-copy attempt raised exception:', e)
            zero_ok = False
        if not zero_ok:
            print('Zero-copy path failed or returned False; proceeding to FBO fallback')
    else:
        print('Zero-copy disabled (default). Using FBO snapshot path.')
    snapshot_png = None
    if zero_ok:
        print('[TRACE] zero-copy path succeeded', flush=True)
    else:
        print('[TRACE] zero-copy failed; falling back to FBO snapshot', flush=True)
        try:
            png_bytes, tex_id = fbo_skia_render_and_snapshot(WIDTH, HEIGHT)
            snapshot_png = png_bytes
            # also save to disk
            with open(OUT, 'wb') as f:
                f.write(png_bytes)
            print('Wrote fallback snapshot to', OUT)
        except Exception as e:
            print('Fallback failed:', e)
            traceback.print_exc()
            # attempt to close window and exit cleanly
            try:
                window.close()
            except Exception:
                pass
            _exit_app()
            sys.exit(1)

    # Now display the texture in pyglet
    # create a pyglet image from texture id (bind to current GL context)
    try:
        # create a TextureRegion pointing at our GL texture id. Pyglet doesn't
        # provide a simple public constructor for wrapping an existing GL texture id
        # reliably across versions, but we can use pyglet.image.Texture.create_for_size
        # in newer versions or construct from ImageData if we have PNG bytes.
        if snapshot_png is not None:
            # we have PNG bytes; load into pyglet image
            bio = io.BytesIO(snapshot_png)
            img = pyglet.image.load(None, file=bio)
        else:
            # Try to create a pyglet texture from GL texture id by creating an ImageData with a custom id.
            # Fallback: read pixels from the texture into a bytes buffer and build ImageData.
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
            buf = (gl.GLubyte * (WIDTH * HEIGHT * 4))()
            gl.glGetTexImage(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, buf)
            data = bytes(buf)
            # Flip the buffer vertically for correct display in pyglet
            flipped = bytearray(len(data))
            row = WIDTH * 4
            for i in range(HEIGHT):
                src_off = (HEIGHT - 1 - i) * row
                dst_off = i * row
                flipped[dst_off:dst_off+row] = data[src_off:src_off+row]
            img = pyglet.image.ImageData(WIDTH, HEIGHT, 'RGBA', bytes(flipped), pitch=WIDTH * 4)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    except Exception as e:
        print('Failed to create pyglet image from texture:', e)
        traceback.print_exc()
        sys.exit(1)

    # If zero-copy succeeded and we have a GL texture id, prepare to draw a textured quad directly.
    use_direct_gl_draw = False
    if args.zero_copy and zero_ok:
        print('Using direct GL texture draw path')
        use_direct_gl_draw = True

    # prepare GL state for drawing textured quad (simple textured fullscreen quad)
    def draw_textured_quad(tex_id):
        # save state
        print('[TRACE] draw_textured_quad start')
        gl.glPushAttrib(gl.GL_ALL_ATTRIB_BITS)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(0, WIDTH, 0, HEIGHT, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0.0, 0.0); gl.glVertex2f(0.0, 0.0)
        gl.glTexCoord2f(1.0, 0.0); gl.glVertex2f(WIDTH, 0.0)
        gl.glTexCoord2f(1.0, 1.0); gl.glVertex2f(WIDTH, HEIGHT)
        gl.glTexCoord2f(0.0, 1.0); gl.glVertex2f(0.0, HEIGHT)
        gl.glEnd()

        # restore matrices
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        # restore attribs
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glPopAttrib()

        # Create a persistent rectangle object
        rect = shapes.Rectangle(250, 300, 400, 200, color=(255, 0, 0))

        @window.event
        def on_draw():
            window.clear()
            # rect.draw()
            # # Optionally, try to blit the Skia image (if available)
            if 'img' in locals() and img is not None:
                img.blit(0, 0)
                print('Window drawn')
    print('Entering pyglet.app.run() event loop. Close the window or press Ctrl-C to exit.')

    # Use pyglet's built-in event loop for proper event dispatching
    pyglet.app.run()


if __name__ == '__main__':
    main()
