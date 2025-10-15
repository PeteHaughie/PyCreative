#!/usr/bin/env python3
"""Probe whether GrGLTextureInfo or GrBackendTexture constructor blocks.

Run under the project venv. The script creates a pyglet window (GL context)
then constructs the two objects separately with trace prints.
"""
import time
import ctypes
import sys
import traceback

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

WIDTH, HEIGHT = 64, 64

print('creating pyglet window')
win = pyglet.window.Window(width=WIDTH, height=HEIGHT, visible=False)
print('window created')

def create_gl_tex():
    tex = gl.GLuint()
    gl.glGenTextures(1, ctypes.byref(tex))
    tid = int(tex.value)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tid)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, WIDTH, HEIGHT, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    return tid

tid = create_gl_tex()
print('created GL texture id', tid)

try:
    print('probe: calling GrDirectContext.MakeGL', flush=True)
    ctx = skia.GrDirectContext.MakeGL()
    print('probe: GrDirectContext.MakeGL returned', 'None' if ctx is None else 'ok', flush=True)
except Exception as e:
    print('probe: MakeGL exception', e)
    traceback.print_exc()

try:
    print('probe: about to construct GrGLTextureInfo', flush=True)
    t0 = time.time()
    gti = skia.GrGLTextureInfo(int(tid), int(gl.GL_RGBA8))
    print('probe: GrGLTextureInfo constructed OK, took', time.time()-t0)
except Exception as e:
    print('probe: GrGLTextureInfo exception', e)
    traceback.print_exc()

try:
    print('probe: about to construct GrBackendTexture', flush=True)
    t0 = time.time()
    bt = skia.GrBackendTexture(WIDTH, HEIGHT, skia.GrMipmapped.kNo, gti)
    print('probe: GrBackendTexture constructed OK, took', time.time()-t0)
except Exception as e:
    print('probe: GrBackendTexture exception', e)
    traceback.print_exc()

print('probe done')
