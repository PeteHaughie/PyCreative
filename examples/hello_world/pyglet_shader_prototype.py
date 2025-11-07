"""Pyglet shader prototype

Compiles an attributeless vertex shader and the fragment shader
from examples/hello_world/data/tint.frag, uploads a test RGBA image
as a GL texture, draws a fullscreen triangle sampling iChannel0, and
reads back the center pixel to verify the shader output.

Run:
    python examples/hello_world/pyglet_shader_prototype.py

Environment:
    Requires pyglet and pillow available in the environment used by
    the project virtualenv. This script is intended to run locally.
"""

from __future__ import annotations
import ctypes
import os
from PIL import Image

import pyglet
from pyglet import gl

WINDOW_W = 640
WINDOW_H = 480
IMG_W = 320
IMG_H = 240

# Attributeless vertex shader (GLSL 150) using gl_VertexID
ATTRLESS_VERT = """#version 150
out vec2 v_texcoord;
void main() {
    int id = int(gl_VertexID);
    if (id == 0) {
        v_texcoord = vec2(0.0, 0.0);
        gl_Position = vec4(-1.0, -1.0, 0.0, 1.0);
    } else if (id == 1) {
        v_texcoord = vec2(2.0, 0.0);
        gl_Position = vec4(3.0, -1.0, 0.0, 1.0);
    } else {
        v_texcoord = vec2(0.0, 2.0);
        gl_Position = vec4(-1.0, 3.0, 0.0, 1.0);
    }
}
"""

# Load fragment shader from examples data
FRAG_PATH = os.path.join(os.path.dirname(__file__), 'data', 'tint.frag')
try:
    with open(FRAG_PATH, 'r', encoding='utf-8') as fh:
        FRAG_SRC = fh.read()
except Exception:
    FRAG_SRC = "#version 150\nout vec4 fragColor;\nvoid main(){ fragColor = vec4(1.0,0.0,1.0,1.0); }"


def compile_shader(src: str, shader_type):
    # strip leading whitespace so #version is at start
    try:
        src = src.lstrip()
    except Exception:
        pass
    src_buf = ctypes.create_string_buffer(src.encode('utf-8'))
    src_ptr = ctypes.cast(ctypes.pointer(ctypes.pointer(src_buf)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
    sh = gl.glCreateShader(shader_type)
    gl.glShaderSource(sh, 1, src_ptr, None)
    gl.glCompileShader(sh)
    status = gl.GLint()
    gl.glGetShaderiv(sh, gl.GL_COMPILE_STATUS, ctypes.byref(status))
    if not bool(status.value):
        log_len = gl.GLint()
        gl.glGetShaderiv(sh, gl.GL_INFO_LOG_LENGTH, ctypes.byref(log_len))
        if log_len.value > 0:
            buf = ctypes.create_string_buffer(log_len.value)
            gl.glGetShaderInfoLog(sh, log_len.value, None, buf)
            raise RuntimeError('Shader compile error:\n' + buf.value.decode('utf-8', 'ignore'))
        raise RuntimeError('Shader compile failed')
    return sh


def link_program(vert, frag):
    prog = gl.glCreateProgram()
    gl.glAttachShader(prog, vert)
    gl.glAttachShader(prog, frag)
    gl.glLinkProgram(prog)
    status = gl.GLint()
    gl.glGetProgramiv(prog, gl.GL_LINK_STATUS, ctypes.byref(status))
    if not bool(status.value):
        log_len = gl.GLint()
        gl.glGetProgramiv(prog, gl.GL_INFO_LOG_LENGTH, ctypes.byref(log_len))
        if log_len.value > 0:
            buf = ctypes.create_string_buffer(log_len.value)
            gl.glGetProgramInfoLog(prog, log_len.value, None, buf)
            raise RuntimeError('Program link error:\n' + buf.value.decode('utf-8', 'ignore'))
        raise RuntimeError('Program link failed')
    return prog


def create_test_image(w, h):
    # simple gradient + green channel to see effect
    im = Image.new('RGBA', (w, h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            r = int(255 * x / max(1, w - 1))
            g = int(255 * y / max(1, h - 1))
            b = 128
            a = 255
            px[x, y] = (r, g, b, a)
    return im


def upload_image_to_texture(img: Image.Image):
    # ensure RGBA
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    data = img.tobytes()
    tex = gl.GLuint()
    gl.glGenTextures(1, ctypes.byref(tex))
    tid = int(tex.value)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tid)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
    arr = (gl.GLubyte * len(data)).from_buffer_copy(data)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, img.width, img.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.byref(arr))
    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 4)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    return tid


def read_center_pixel(w, h):
    # read center pixel from current framebuffer
    cx = max(0, w // 2)
    cy = max(0, h // 2)
    buf = (gl.GLubyte * 4)()
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
    gl.glReadPixels(cx, cy, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.byref(buf))
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 4)
    return (int(buf[0]), int(buf[1]), int(buf[2]), int(buf[3]))


class PrototypeWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(width=WINDOW_W, height=WINDOW_H, caption='pyglet shader prototype')
        self.img = create_test_image(IMG_W, IMG_H)
        self.tex = None
        self.prog = None
        self.setup_gl()

    def setup_gl(self):
        # compile shaders
        try:
            vsh = compile_shader(ATTRLESS_VERT, gl.GL_VERTEX_SHADER)
            fsh = compile_shader(FRAG_SRC, gl.GL_FRAGMENT_SHADER)
            self.prog = link_program(vsh, fsh)
            print('Compiled program', int(self.prog))
        except Exception as e:
            print('Shader compile/link failed:', e)
            raise

        # upload texture
        self.tex = upload_image_to_texture(self.img)
        # create and bind a VAO (needed on core profiles for gl_VertexID draws)
        try:
            if hasattr(gl, 'glGenVertexArrays') and hasattr(gl, 'glBindVertexArray'):
                vao = gl.GLuint()
                gl.glGenVertexArrays(1, ctypes.byref(vao))
                self._vao = int(vao.value)
                try:
                    gl.glBindVertexArray(self._vao)
                except Exception:
                    pass
            else:
                self._vao = None
        except Exception:
            self._vao = None

    def on_draw(self):
        self.clear()
        # Bind program and texture, draw fullscreen triangle
        try:
            prev_prog = gl.GLint()
            gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM, ctypes.byref(prev_prog))
        except Exception:
            prev_prog = None
        try:
            gl.glUseProgram(int(self.prog))
        except Exception:
            pass
        try:
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, int(self.tex))
            # set sampler uniform if present
            try:
                loc = gl.glGetUniformLocation(int(self.prog), b'iChannel0')
                if int(loc) != -1:
                    gl.glUniform1i(int(loc), 0)
            except Exception:
                pass
            # Ensure a VAO is bound for core profile compatibility
            try:
                if getattr(self, '_vao', None):
                    gl.glBindVertexArray(int(self._vao))
            except Exception:
                pass
            # draw
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
        except Exception as e:
            print('Draw failed:', e)
        finally:
            try:
                if prev_prog is not None:
                    gl.glUseProgram(int(prev_prog))
                else:
                    gl.glUseProgram(0)
            except Exception:
                pass

        # read back center pixel from default framebuffer
        try:
            rgba = read_center_pixel(WINDOW_W, WINDOW_H)
            print('Readback center pixel RGBA:', rgba)
        except Exception as e:
            print('Readback failed:', e)

        # keep window open briefly; exit after drawing once
        pyglet.app.exit()


if __name__ == '__main__':
    win = PrototypeWindow()
    pyglet.app.run()
