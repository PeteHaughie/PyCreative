"""Minimal Pyglet-based presenter used for prototyping shader rendering.

This presenter intentionally implements a very small subset of the
Skia presenter API: it accepts recorded commands (a list of ops), looks
for a `shader` followed by an `image` op and renders the image through
the shader into the current GL default framebuffer using a
fullscreen-triangle (gl_VertexID) approach.

This is a prototype: it focuses on correctness and portability rather
than full feature parity with SkiaGLPresenter.
"""
from __future__ import annotations

import ctypes
import logging
import os
from typing import Any, Sequence

from pyglet import gl


class PygletPresenter:
    def __init__(self, width: int, height: int, *, force_present_mode=None, force_gles=False, window=None):
        self.width = int(width)
        self.height = int(height)
        self._window = window
        self._prog = None
        self._vao = None
        self._compiled_variant = None
        # Pre-created attributeless vertex shader source (GLSL 150)
        self._attrless_vert = """#version 150
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

    def resize(self, w: int, h: int):
        try:
            self.width = int(w)
            self.height = int(h)
        except Exception:
            pass

    def _compile_shader(self, src: str, shader_type):
        # ensure #version at start when possible
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
                raise RuntimeError(buf.value.decode('utf-8', 'ignore'))
            raise RuntimeError('Shader compile failed')
        return sh

    def _link_program(self, vert, frag):
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
                raise RuntimeError(buf.value.decode('utf-8', 'ignore'))
            raise RuntimeError('Program link failed')
        return prog

    def _ensure_vao(self):
        try:
            if getattr(self, '_vao', None) is None and hasattr(gl, 'glGenVertexArrays'):
                vao = gl.GLuint()
                gl.glGenVertexArrays(1, ctypes.byref(vao))
                self._vao = int(vao.value)
                try:
                    gl.glBindVertexArray(int(self._vao))
                except Exception:
                    pass
        except Exception:
            self._vao = None

    def _use_program_for_frag(self, frag_src: str):
        # compile/link frag with attributeless vertex shader
        try:
            vsh = self._compile_shader(self._attrless_vert, gl.GL_VERTEX_SHADER)
            # ensure frag has a #version if not present
            if '#version' not in (frag_src or ''):
                fsrc = '#version 150\n' + (frag_src or '').lstrip()
            else:
                fsrc = frag_src
            fsh = self._compile_shader(fsrc, gl.GL_FRAGMENT_SHADER)
            prog = self._link_program(vsh, fsh)
            self._prog = int(prog)
            self._compiled_variant = '150'
            logging.getLogger(__name__).debug('PygletPresenter: compiled fragment into prog=%s', int(prog))
            return True
        except Exception as e:
            logging.getLogger(__name__).debug('PygletPresenter: frag compile/link failed: %r', e)
            self._prog = None
            return False

    def render_commands(self, commands: Sequence[dict], replay_fn) -> None:
        # Simple pre-processing: look for shader then image op pair
        bound_shader = None
        processed = False
        for cmd in list(commands):
            op = cmd.get('op')
            args = cmd.get('args', {}) or {}
            if op == 'shader':
                bound_shader = args.get('shader')
            if op == 'image' and bound_shader is not None:
                # prefer raw bytes
                ib = args.get('image_bytes')
                isize = args.get('image_size')
                if not ib and args.get('image') is not None:
                    try:
                        from PIL import Image as _PILImage
                        _img = args.get('image')
                        if isinstance(_img, _PILImage):
                            if _img.mode != 'RGBA':
                                _img = _img.convert('RGBA')
                            ib = _img.tobytes()
                            isize = (_img.width, _img.height)
                    except Exception:
                        ib = None
                if ib and isize:
                    # compile frag if needed
                    try:
                        frag_src = getattr(bound_shader, 'frag_source', '') or ''
                    except Exception:
                        frag_src = ''
                    ok = self._use_program_for_frag(frag_src)
                    if not ok:
                        # fallback: nothing to do, let replay_fn handle it
                        break
                    # upload texture and draw
                    try:
                        # upload
                        tex = gl.GLuint()
                        gl.glGenTextures(1, ctypes.byref(tex))
                        tid = int(tex.value)
                        gl.glBindTexture(gl.GL_TEXTURE_2D, tid)
                        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
                        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
                        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
                        arr = (gl.GLubyte * len(ib)).from_buffer_copy(ib)
                        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, int(isize[0]), int(isize[1]), 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.byref(arr))
                        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 4)
                        # ensure VAO
                        self._ensure_vao()
                        # draw
                        try:
                            gl.glUseProgram(int(self._prog))
                        except Exception:
                            pass
                        try:
                            gl.glActiveTexture(gl.GL_TEXTURE0)
                            gl.glBindTexture(gl.GL_TEXTURE_2D, tid)
                        except Exception:
                            pass
                        try:
                            loc = gl.glGetUniformLocation(int(self._prog), b'iChannel0')
                            if int(loc) != -1:
                                gl.glUniform1i(int(loc), 0)
                        except Exception:
                            pass
                        try:
                            if getattr(self, '_vao', None):
                                try:
                                    gl.glBindVertexArray(int(self._vao))
                                except Exception:
                                    pass
                            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
                        except Exception:
                            pass
                        try:
                            # readback center pixel for diagnostic
                            buf = (gl.GLubyte * 4)()
                            vp = (gl.GLint * 4)()
                            try:
                                gl.glGetIntegerv(gl.GL_VIEWPORT, vp)
                                rw, rh = int(vp[2]), int(vp[3])
                            except Exception:
                                rw, rh = self.width, self.height
                            cx = max(0, rw // 2)
                            cy = max(0, rh // 2)
                            gl.glReadPixels(cx, cy, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.byref(buf))
                            logging.getLogger(__name__).debug('PygletPresenter: readback center rgba=%r', (int(buf[0]), int(buf[1]), int(buf[2]), int(buf[3])))
                        except Exception:
                            pass
                        try:
                            gl.glUseProgram(0)
                        except Exception:
                            pass
                        try:
                            tdel = gl.GLuint(tid)
                            gl.glDeleteTextures(1, ctypes.byref(tdel))
                        except Exception:
                            pass
                        processed = True
                        # We've handled this image via GL; don't let replay_fn duplicate it
                        break
                    except Exception:
                        # fall back to replay_fn
                        break
        if not processed:
            try:
                # Fall back to replay_fn for commands we didn't handle
                replay_fn(commands, None)
            except Exception:
                pass

    def present(self) -> bool:
        # For windowed runs the windowing system swaps buffers. Return
        # False to indicate no resize occurred.
        try:
            return False
        except Exception:
            return False

    def teardown(self):
        try:
            if getattr(self, '_vao', None):
                try:
                    vao = gl.GLuint(int(self._vao))
                    gl.glDeleteVertexArrays(1, ctypes.byref(vao))
                except Exception:
                    pass
        except Exception:
            pass
*** End Patch