#!/usr/bin/env python3
"""Attempt to create a Skia backend texture and surface in an isolated process.

This script creates a pyglet window (GL context), creates a GL texture, then
attempts the skia.GrGLTextureInfo -> skia.GrBackendTexture ->
skia.Surface.MakeFromBackendTexture flow. It prints trace lines before and
after each step so callers can see where it blocks or fails.

Usage: python scripts/attempt_backend_texture.py
"""
import time
import ctypes
import traceback
import io
import sys

try:
    import pyglet
    from pyglet import gl
except Exception as e:
    print('PYGLET_IMPORT_ERROR', e)
    sys.exit(2)

try:
    import skia
except Exception as e:
    print('SKIA_IMPORT_ERROR', e)
    sys.exit(3)

WIDTH, HEIGHT = 640, 480

def create_gl_texture(w, h):
    tex = gl.GLuint()
    gl.glGenTextures(1, ctypes.byref(tex))
    tex_id = int(tex.value)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    return tex_id

def main():
    print('creating pyglet window', flush=True)
    window = pyglet.window.Window(width=WIDTH, height=HEIGHT, caption='attempt_backend_texture', visible=False)
    print('window created', flush=True)

    print('created GL texture id probe', flush=True)
    tex_id = create_gl_texture(WIDTH, HEIGHT)
    print('created GL texture id', tex_id, flush=True)

    try:
        print('probe: calling GrDirectContext.MakeGL', flush=True)
        ctx = skia.GrDirectContext.MakeGL()
        print('probe: GrDirectContext.MakeGL returned', 'None' if ctx is None else 'ok', flush=True)
        if ctx is None:
            print('probe: no GL context available for skia', flush=True)
            sys.exit(4)

        # choose mip enum
        try:
            mip = skia.GrMipmapped.kNo
        except Exception:
            try:
                mip = skia.GrMipMapped.kNo
            except Exception:
                mip = 0

        print('probe: about to construct GrGLTextureInfo', flush=True)
        t0 = time.time()
        try:
            tex_info = skia.GrGLTextureInfo(int(tex_id), int(gl.GL_RGBA8))
            print('probe: GrGLTextureInfo constructed OK, took', time.time() - t0, flush=True)
        except Exception as e:
            print('probe: GrGLTextureInfo constructor raised', e, flush=True)
            traceback.print_exc()
            sys.exit(5)

        print('probe: about to construct GrBackendTexture', flush=True)
        t0 = time.time()
        try:
            backend_tex = skia.GrBackendTexture(WIDTH, HEIGHT, mip, tex_info)
            print('probe: GrBackendTexture constructed OK, took', time.time() - t0, flush=True)
        except Exception as e:
            print('probe: GrBackendTexture constructor raised', e, flush=True)
            traceback.print_exc()
            sys.exit(6)

        print('probe: calling MakeFromBackendTexture', flush=True)
        try:
            surf = skia.Surface.MakeFromBackendTexture(ctx, backend_tex, skia.kTopLeft_GrSurfaceOrigin, skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB(), {})
            print('probe: MakeFromBackendTexture returned', 'None' if surf is None else 'ok', flush=True)
            if surf is None:
                sys.exit(7)
        except Exception as e:
            print('probe: MakeFromBackendTexture raised', e, flush=True)
            traceback.print_exc()
            sys.exit(8)

        print('probe: drawing and flushing', flush=True)
        try:
            canvas = surf.getCanvas()
            p = skia.Paint()
            p.setColor(skia.Color4f(1,0,0,1))
            try:
                p.setAntiAlias(True)
            except Exception:
                pass
            canvas.drawRect(skia.Rect.MakeXYWH(10,10,100,100), p)
            ctx.flush()
            print('probe: draw+flush ok', flush=True)
        except Exception as e:
            print('probe: draw+flush error', e, flush=True)
            traceback.print_exc()
            sys.exit(9)

        # success
        print('probe: success', flush=True)
        sys.exit(0)

    except Exception as e:
        print('probe: unexpected exception', e, flush=True)
        traceback.print_exc()
        sys.exit(10)

if __name__ == '__main__':
    main()
