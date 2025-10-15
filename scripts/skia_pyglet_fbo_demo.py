#!/usr/bin/env python3
"""Persistent FBO demo: Skia draws into a GL texture (via an attached FBO) and
pyglet displays the texture each frame. The FBO and texture are created once
and reused across frames. Clean teardown is implemented.

Auto-exits after a short time so it is safe to run in automated environments.
"""
from __future__ import annotations

import time
import math
import ctypes
import sys
import traceback
import os

try:
    import skia
except Exception:
    skia = None

import pyglet
from pyglet import gl
from core.adapters.skia_gl_present import SkiaGLPresenter

WIDTH, HEIGHT = 640, 480
RUN_SECONDS = 12.0
CAPTURE_EVERY_N = 5
MAX_CAPTURES = 12
FORCE_PER_FRAME_SURFACE = True

# Simple passthrough shaders for textured quad
def draw_textured_quad(tex_id, w=WIDTH, h=HEIGHT):
    """Draw a full-window textured quad using the fixed-function pipeline.
    This avoids shader/VBO setup and works as a simple present path for
    drivers where shaders are problematic.
    """
    try:
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, int(tex_id))
        # set up orthographic projection matching window pixels
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(0, w, 0, h, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0.0, 0.0); gl.glVertex2f(0.0, 0.0)
        gl.glTexCoord2f(1.0, 0.0); gl.glVertex2f(w, 0.0)
        gl.glTexCoord2f(1.0, 1.0); gl.glVertex2f(w, h)
        gl.glTexCoord2f(0.0, 1.0); gl.glVertex2f(0.0, h)
        gl.glEnd()

        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glDisable(gl.GL_TEXTURE_2D)
    except Exception:
        # Let caller fallback to readback path
        raise



def create_gl_texture(w, h):
    tex = gl.GLuint()
    gl.glGenTextures(1, ctypes.byref(tex))
    tex_id = int(tex.value)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    return tex_id


def create_fbo_for_texture(tex_id):
    fbo = gl.GLuint()
    gl.glGenFramebuffers(1, ctypes.byref(fbo))
    fbo_id = int(fbo.value)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo_id)
    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, int(tex_id), 0)
    status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
    if status != gl.GL_FRAMEBUFFER_COMPLETE:
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        raise RuntimeError('FBO incomplete: %r' % (status,))
    # leave it bound for the caller to use
    return fbo_id


# draw_textured_quad implemented above; legacy shader/VBO paths removed


def make_paint(r, g, b, a=1.0, stroke=False, stroke_width=1.0):
    p = skia.Paint()
    try:
        p.setAntiAlias(True)
    except Exception:
        pass
    try:
        p.setColor(skia.Color4f(r, g, b, a))
    except Exception:
        try:
            icol = (int(a * 255) << 24) | (int(r * 255) << 16) | (int(g * 255) << 8) | int(b * 255)
            p.setColor(icol)
        except Exception:
            pass
    try:
        if stroke:
            p.setStyle(skia.Paint.kStroke_Style)
            p.setStrokeWidth(float(stroke_width))
        else:
            p.setStyle(skia.Paint.kFill_Style)
    except Exception:
        pass
    return p


def main():
    if skia is None:
        print('skia-python not installed in this environment')
        sys.exit(1)

    window = pyglet.window.Window(width=WIDTH, height=HEIGHT, caption='Skia FBO persistent demo')

    # Use the SkiaGLPresenter adapter to manage FBO/texture and Skia surface.
    print('creating SkiaGLPresenter and GL resources', flush=True)
    presenter = SkiaGLPresenter(WIDTH, HEIGHT)
    try:
        presenter.ensure_resources()
    except Exception:
        # allow the demo to continue; ensure_resources can raise on odd drivers
        traceback.print_exc()
    tex_id = presenter.tex_id
    fbo_id = presenter.fbo_id
    ctx = presenter.gr_context
    print('presenter tex', tex_id, 'fbo', fbo_id, 'ctx', bool(ctx), flush=True)

    # Using fixed-function textured-quad present path (no shaders/VBOs).
    print('Using fixed-function textured-quad present path (no shaders)', flush=True)

    # prepare a persistent pyglet texture for the readback fallback
    try:
        zero = (b'\x00' * (WIDTH * HEIGHT * 4))
        img0 = pyglet.image.ImageData(WIDTH, HEIGHT, 'RGBA', zero, pitch=-WIDTH * 4)
        fallback_texture = img0.get_texture()
        upload_buf = bytearray(WIDTH * HEIGHT * 4)
    except Exception:
        fallback_texture = None
        upload_buf = None

    start = time.time()
    angle = 0.0
    running = True
    frame_idx = 0
    save_first_n = 3

    def draw_skia_frame(canvas, frame_idx_local, angle_local):
        """Draw the same content previously drawn inline into Skia canvas.
        This helper lets the presenter call into the Skia drawing code.
        """
        # diagnostic log: note that we're drawing this frame
        try:
            print(f'skia: drawing frame {frame_idx_local} angle={angle_local:.3f}', flush=True)
        except Exception:
            pass
        # clear to a varying background so we can detect per-frame updates
        try:
            bg = 0.05 + (frame_idx_local % 60) / 60.0 * 0.6
            canvas.clear(skia.Color4f(bg, bg * 0.9, bg * 0.8, 1.0))
        except Exception:
            try:
                ival = int(0x10 + (frame_idx_local % 60))
                canvas.clear((0xFF << 24) | (ival << 16) | (ival << 8) | ival)
            except Exception:
                pass

        # moving circle
        cx = WIDTH / 2 + math.cos(angle_local) * 160
        cy = HEIGHT / 2 + math.sin(angle_local) * 120
        r = 48
        fill = make_paint(0.2, 0.7, 0.9, 1.0, stroke=False)
        canvas.drawCircle(cx, cy, r, fill)

        stroke = make_paint(1.0, 1.0, 1.0, 1.0, stroke=True, stroke_width=3.0)
        canvas.drawCircle(cx, cy, r, stroke)

        # small rotating cross
        cross_p = make_paint(1.0, 0.5, 0.2, 1.0, stroke=True, stroke_width=2.0)
        canvas.save()
        canvas.translate(cx, cy)
        canvas.rotate(angle_local * 45.0)
        canvas.drawLine(-20, 0, 20, 0, cross_p)
        canvas.drawLine(0, -20, 0, 20, cross_p)
        canvas.restore()
        # test primitive: small static red rectangle near bottom-left
        try:
            test_p = make_paint(1.0, 0.0, 0.0, 1.0, stroke=False)
            canvas.drawRect(10, 10, 30, 30, test_p)
        except Exception:
            pass

    def _exit(dt=0):
        # signal stop; actual GL resource cleanup happens after the loop
        nonlocal running
        running = False
        try:
            if not window.has_exit:
                window.close()
        except Exception:
            pass

    # schedule an auto-exit so CI doesn't hang
    pyglet.clock.schedule_once(_exit, RUN_SECONDS)

    # main loop: update and draw
    try:
        while running and not window.has_exit:
            # run pyglet clock so scheduled callbacks (auto-exit) fire
            try:
                pyglet.clock.tick()
            except Exception:
                pass
            now = time.time()
            # target 30 FPS for clearer per-frame deltas
            dt = 1.0 / 30.0
            angle += dt * 1.2

            # bind FBO and let Skia draw into it
            try:
                # Try the simple fixed-function textured-quad present first
                try:
                    draw_textured_quad(tex_id)
                except Exception:
                    # Fallback: read back FBO pixels and upload to pyglet for display
                    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo_id)
                    try:
                        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
                    except Exception:
                        pass
                    buf = (gl.GLubyte * (WIDTH * HEIGHT * 4))()
                    gl.glReadPixels(0, 0, WIDTH, HEIGHT, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, buf)
                    raw = bytes(buf)
                    # Flip the buffer vertically for correct display in pyglet
                    flipped = bytearray(len(raw))
                    row = WIDTH * 4
                    for i in range(HEIGHT):
                        src_off = (HEIGHT - 1 - i) * row
                        dst_off = i * row
                        flipped[dst_off:dst_off+row] = raw[src_off:src_off+row]
                    # diagnostics: checksum / mean and optional save of first frames
                    try:
                        import hashlib
                        import statistics
                        arr = raw
                        chksum = hashlib.md5(arr).hexdigest()
                        vals = memoryview(arr)
                        r_vals = [vals[i] for i in range(0, len(arr), 4)]
                        mean_r = statistics.mean(r_vals) if r_vals else 0
                        print(f'frame[{frame_idx}] readback md5={chksum} meanR={mean_r}', flush=True)
                        if (frame_idx < save_first_n) or (frame_idx % CAPTURE_EVERY_N == 0 and frame_idx // CAPTURE_EVERY_N < MAX_CAPTURES):
                            try:
                                from PIL import Image, ImageChops
                                img_p = Image.frombytes('RGBA', (WIDTH, HEIGHT), raw)
                                img_p = img_p.transpose(Image.FLIP_TOP_BOTTOM)
                                fname = f'skia_fbo_frame_{frame_idx}.png'
                                img_p.save(fname)
                                print('wrote', fname, flush=True)
                                sname = f'skia_snapshot_frame_{frame_idx}.png'
                                if os.path.exists(sname):
                                    try:
                                        simg = Image.open(sname).convert('RGBA')
                                        if simg.size != img_p.size:
                                            print('size mismatch between skia snapshot and readback', flush=True)
                                        else:
                                            diff = ImageChops.difference(simg, img_p)
                                            b = diff.getbbox()
                                            if b is None:
                                                print(f'frame[{frame_idx}] SKIA snapshot == GL readback (exact match)', flush=True)
                                            else:
                                                dname = f'skia_diff_frame_{frame_idx}.png'
                                                diff.save(dname)
                                                print(f'frame[{frame_idx}] diff saved to', dname, 'bbox=', b, flush=True)
                                    except Exception:
                                        pass
                                try:
                                    sx = 15
                                    sy = 15
                                    idx = (sy * WIDTH + sx) * 4
                                    if idx + 3 < len(raw):
                                        r0 = raw[idx]
                                        g0 = raw[idx+1]
                                        b0 = raw[idx+2]
                                        a0 = raw[idx+3]
                                        print(f'frame[{frame_idx}] test-pixel RGBA at (15,15)=', (r0, g0, b0, a0), flush=True)
                                except Exception:
                                    pass
                            except Exception:
                                pass
                    except Exception:
                        pass
                    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
                    if fallback_texture is not None and upload_buf is not None:
                        # Use the already-flipped buffer for display
                        try:
                            fallback_texture.blit_into(bytes(flipped), 0, 0, 0)
                            fallback_texture.blit(0, 0)
                        except Exception:
                            img = pyglet.image.ImageData(WIDTH, HEIGHT, 'RGBA', bytes(flipped), pitch=WIDTH * 4)
                            img.blit(0, 0)
                    else:
                        img = pyglet.image.ImageData(WIDTH, HEIGHT, 'RGBA', bytes(flipped), pitch=WIDTH * 4)
                        img.blit(0, 0)
            except Exception:
                pass

            # draw the texture to screen by reading the FBO and blitting via pyglet.ImageData
            window.dispatch_events()
            window.clear()
            try:
                # Try the simple fixed-function textured-quad present first
                try:
                    draw_textured_quad(tex_id)
                except Exception:
                    # Fallback: read back FBO pixels and upload to pyglet for display
                    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo_id)
                    try:
                        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
                    except Exception:
                        pass
                    buf = (gl.GLubyte * (WIDTH * HEIGHT * 4))()
                    gl.glReadPixels(0, 0, WIDTH, HEIGHT, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, buf)
                    raw = bytes(buf)
                    # diagnostics: checksum / mean and optional save of first frames
                    try:
                        import hashlib
                        import statistics
                        arr = raw
                        chksum = hashlib.md5(arr).hexdigest()
                        vals = memoryview(arr)
                        r_vals = [vals[i] for i in range(0, len(arr), 4)]
                        mean_r = statistics.mean(r_vals) if r_vals else 0
                        print(f'frame[{frame_idx}] readback md5={chksum} meanR={mean_r}', flush=True)
                        if (frame_idx < save_first_n) or (frame_idx % CAPTURE_EVERY_N == 0 and frame_idx // CAPTURE_EVERY_N < MAX_CAPTURES):
                            try:
                                from PIL import Image, ImageChops
                                img_p = Image.frombytes('RGBA', (WIDTH, HEIGHT), raw)
                                img_p = img_p.transpose(Image.FLIP_TOP_BOTTOM)
                                fname = f'skia_fbo_frame_{frame_idx}.png'
                                img_p.save(fname)
                                print('wrote', fname, flush=True)
                                sname = f'skia_snapshot_frame_{frame_idx}.png'
                                if os.path.exists(sname):
                                    try:
                                        simg = Image.open(sname).convert('RGBA')
                                        if simg.size != img_p.size:
                                            print('size mismatch between skia snapshot and readback', flush=True)
                                        else:
                                            diff = ImageChops.difference(simg, img_p)
                                            b = diff.getbbox()
                                            if b is None:
                                                print(f'frame[{frame_idx}] SKIA snapshot == GL readback (exact match)', flush=True)
                                            else:
                                                dname = f'skia_diff_frame_{frame_idx}.png'
                                                diff.save(dname)
                                                print(f'frame[{frame_idx}] diff saved to', dname, 'bbox=', b, flush=True)
                                    except Exception:
                                        pass
                                try:
                                    sx = 15
                                    sy = 15
                                    idx = (sy * WIDTH + sx) * 4
                                    if idx + 3 < len(raw):
                                        r0 = raw[idx]
                                        g0 = raw[idx+1]
                                        b0 = raw[idx+2]
                                        a0 = raw[idx+3]
                                        print(f'frame[{frame_idx}] test-pixel RGBA at (15,15)=', (r0, g0, b0, a0), flush=True)
                                except Exception:
                                    pass
                            except Exception:
                                pass
                    except Exception:
                        pass
                    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
                    if fallback_texture is not None and upload_buf is not None:
                        row = WIDTH * 4
                        for i in range(HEIGHT):
                            src_off = (HEIGHT - 1 - i) * row
                            dst_off = i * row
                            upload_buf[dst_off:dst_off+row] = raw[src_off:src_off+row]
                        try:
                            fallback_texture.blit_into(bytes(upload_buf), 0, 0, 0)
                            fallback_texture.blit(0, 0)
                        except Exception:
                            img = pyglet.image.ImageData(WIDTH, HEIGHT, 'RGBA', raw, pitch=-WIDTH * 4)
                            img.blit(0, 0)
                    else:
                        img = pyglet.image.ImageData(WIDTH, HEIGHT, 'RGBA', raw, pitch=-WIDTH * 4)
                        img.blit(0, 0)
            except Exception:
                traceback.print_exc()
            try:
                window.flip()
            except Exception:
                break
            # advance frame counter and sleep to cap frame rate
            frame_idx += 1
            time.sleep(dt)

    except KeyboardInterrupt:
        _exit()
    finally:
        # final cleanup of GL + Skia resources (do this after loop stops)
        try:
            print('cleanup: presenter teardown', flush=True)
            presenter.teardown()
        except Exception:
            # fallback to direct deletion if presenter teardown is unavailable
            try:
                print('fallback cleanup: deleting fbo and texture', flush=True)
                t = gl.GLuint(int(tex_id))
                gl.glDeleteTextures(1, ctypes.byref(t))
            except Exception:
                pass
            try:
                f = gl.GLuint(int(fbo_id))
                gl.glDeleteFramebuffers(1, ctypes.byref(f))
            except Exception:
                pass
            try:
                if hasattr(ctx, 'abandonContext'):
                    ctx.abandonContext()
                elif hasattr(ctx, 'releaseResourcesAndAbandonContext'):
                    ctx.releaseResourcesAndAbandonContext()
            except Exception:
                pass
        try:
            if not window.has_exit:
                window.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
