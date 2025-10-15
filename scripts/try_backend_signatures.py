#!/usr/bin/env python3
"""Try several GrBackendTexture constructor signatures in isolated subprocesses.

Each candidate is run in its own process (using the project venv python) with a short
timeout so a blocking native call won't hang the test runner.

Usage:
    python scripts/try_backend_signatures.py --python /path/to/python
"""
import subprocess
import sys
import textwrap
import argparse
from pathlib import Path

DEFAULT_PY = sys.executable

SCRIPT = textwrap.dedent("""
import sys, time, ctypes, traceback
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

def create_gl_texture(w,h):
    tex = gl.GLuint()
    gl.glGenTextures(1, ctypes.byref(tex))
    tex_id = int(tex.value)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    return tex_id

window = pyglet.window.Window(width=WIDTH, height=HEIGHT, visible=False)
tex_id = create_gl_texture(WIDTH, HEIGHT)
ctx = skia.GrDirectContext.MakeGL()
if ctx is None:
    print('NO_SKIA_GL_CTX')
    sys.exit(4)
try:
    mip = skia.GrMipmapped.kNo
except Exception:
    try:
        mip = skia.GrMipMapped.kNo
    except Exception:
        mip = 0
try:
    tex_info = skia.GrGLTextureInfo(int(tex_id), int(gl.GL_RGBA8))
except Exception as e:
    print('TEXINFO_ERROR', e)
    traceback.print_exc()
    sys.exit(5)

_expr = '''REPLACE_EXPR'''
print('EVAL_EXPR', _expr)
try:
    t0 = time.time()
    res = eval(_expr)
    dt = time.time() - t0
    print('EVAL_OK', dt, repr(res))
except Exception as e:
    print('EVAL_ERROR', e)
    traceback.print_exc()
    sys.exit(6)

""")

CASES = [
    "skia.GrBackendTexture(WIDTH, HEIGHT, mip, tex_info)",
    "skia.GrBackendTexture(WIDTH, HEIGHT, tex_info)",
    "skia.GrBackendTexture(WIDTH, HEIGHT, 0, tex_info)",
    "skia.GrBackendTexture.MakeGL(WIDTH, HEIGHT, False, int(tex_id))",
]

def run_case(python, expr, timeout=3.0):
    code = SCRIPT.replace('REPLACE_EXPR', expr)
    proc = subprocess.Popen([python, '-u', '-c', code], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        out, _ = proc.communicate(timeout=timeout)
        return proc.returncode, out
    except subprocess.TimeoutExpired:
        proc.kill()
        return None, f'TIMEOUT after {timeout}s'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--python', default=DEFAULT_PY)
    p.add_argument('--timeout', type=float, default=3.0)
    args = p.parse_args()

    python = args.python
    print('Using python:', python)
    for expr in CASES:
        print('\n--- TRYING:', expr)
        rc, out = run_case(python, expr, timeout=args.timeout)
        print('RETURN CODE:', rc)
        print(out)

if __name__ == '__main__':
    main()
