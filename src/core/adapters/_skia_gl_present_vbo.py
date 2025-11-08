"""GL shader/VBO helpers factored out from skia_gl_present.

These functions operate on a presenter instance passed as the first
argument and mutate its attributes as the original methods did.
"""
from __future__ import annotations

import ctypes
import logging
from typing import Any


def _compile_shader(presenter: Any, source: str, shader_type):
    from pyglet import gl
    try:
        source = source.lstrip()
    except Exception:
        pass
    src_buf = ctypes.create_string_buffer(source.encode('utf-8'))
    src_ptr = ctypes.cast(ctypes.pointer(ctypes.pointer(src_buf)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, 1, src_ptr, None)
    gl.glCompileShader(shader)
    status = gl.GLint()
    gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ctypes.byref(status))
    if not bool(status.value):
        log_len = gl.GLint()
        gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, ctypes.byref(log_len))
        if log_len.value > 0:
            buf = ctypes.create_string_buffer(log_len.value)
            gl.glGetShaderInfoLog(shader, log_len.value, None, buf)
            msg = buf.value.decode('utf-8', 'ignore')
            try:
                logging.getLogger(__name__).debug('VBO shader compile log: %s', msg)
            except Exception:
                pass
            raise RuntimeError('Shader compile error: ' + msg)
        raise RuntimeError('Shader compile failed')
    return shader


def _link_program(presenter: Any, vert, frag, bind_attribs=None):
    from pyglet import gl
    prog = gl.glCreateProgram()
    gl.glAttachShader(prog, vert)
    gl.glAttachShader(prog, frag)
    if bind_attribs:
        for idx, name in enumerate(bind_attribs):
            try:
                gl.glBindAttribLocation(prog, int(idx), name.encode('utf-8'))
            except Exception:
                try:
                    gl.glBindAttribLocation(prog, int(idx), name)
                except Exception:
                    pass
    gl.glLinkProgram(prog)
    status = gl.GLint()
    gl.glGetProgramiv(prog, gl.GL_LINK_STATUS, ctypes.byref(status))
    if not bool(status.value):
        log_len = gl.GLint()
        gl.glGetProgramiv(prog, gl.GL_INFO_LOG_LENGTH, ctypes.byref(log_len))
        if log_len.value > 0:
            buf = ctypes.create_string_buffer(log_len.value)
            gl.glGetProgramInfoLog(prog, log_len.value, None, buf)
            msg = buf.value.decode('utf-8', 'ignore')
            try:
                logging.getLogger(__name__).debug('VBO program link log: %s', msg)
            except Exception:
                pass
            raise RuntimeError('Program link error: ' + msg)
        raise RuntimeError('Program link failed')
    return prog


def _ensure_textured_quad_resources(presenter: Any):
    """Create GLSL program and a static VBO for a fullscreen quad.

    Mutates presenter._fs_prog, _fs_vbo, _fs_vao and related attrib/locs.
    """
    if getattr(presenter, '_fs_prog', None) is not None and getattr(presenter, '_fs_vbo', None) is not None:
        return
    from pyglet import gl

    # variant sources
    vs150 = '''#version 150
in vec2 a_pos;
in vec2 a_uv;
out vec2 v_uv;
uniform float u_flip_y;
void main() {
    v_uv = a_uv;
    if (u_flip_y < 0.5) {
        v_uv.y = 1.0 - v_uv.y;
    }
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
'''
    fs150 = '''#version 150
in vec2 v_uv;
out vec4 fragColor;
uniform sampler2D u_tex;
void main() {
    vec4 c = texture(u_tex, v_uv);
    fragColor = c;
}
'''

    vs_es300 = '''#version 300 es
in vec2 a_pos;
in vec2 a_uv;
out vec2 v_uv;
uniform float u_flip_y;
void main() {
    v_uv = a_uv;
    if (u_flip_y < 0.5) {
        v_uv.y = 1.0 - v_uv.y;
    }
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
'''
    fs_es300 = '''#version 300 es
precision mediump float;
in vec2 v_uv;
uniform sampler2D u_tex;
out vec4 fragColor;
void main() {
    vec4 c = texture(u_tex, v_uv);
    fragColor = c;
}
'''

    vs120 = '''#version 120
attribute vec2 a_pos;
attribute vec2 a_uv;
varying vec2 v_uv;
uniform float u_flip_y;
void main() {
    v_uv = a_uv;
    if (u_flip_y < 0.5) {
        v_uv.y = 1.0 - v_uv.y;
    }
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
'''
    fs120 = '''#version 120
varying vec2 v_uv;
uniform sampler2D u_tex;
void main() {
    vec4 c = texture2D(u_tex, v_uv);
    gl_FragColor = c;
}
'''

    variants = []
    try:
        prefer_es = bool(getattr(presenter, 'force_gles', False)) or presenter._sniff_gles3_support()
    except Exception:
        prefer_es = bool(getattr(presenter, 'force_gles', False))
    if prefer_es:
        variants.extend([
            ('es300', vs_es300, fs_es300),
            ('150', vs150, fs150),
            ('120', vs120, fs120),
        ])
    else:
        variants.extend([
            ('150', vs150, fs150),
            ('es300', vs_es300, fs_es300),
            ('120', vs120, fs120),
        ])
    last_exc = None
    vert = None
    frag = None
    prog = None
    for tag, vs_src, fs_src in variants:
        try:
            vert = _compile_shader(presenter, vs_src, gl.GL_VERTEX_SHADER)
            frag = _compile_shader(presenter, fs_src, gl.GL_FRAGMENT_SHADER)
            prog = _link_program(presenter, vert, frag, bind_attribs=['a_pos', 'a_uv'])
            try:
                logging.getLogger(__name__).debug('Compiled shader variant GLSL %s', tag)
            except Exception:
                pass
            break
        except Exception as e:
            last_exc = e
            try:
                if vert is not None:
                    gl.glDeleteShader(vert)
            except Exception:
                pass
            try:
                if frag is not None:
                    gl.glDeleteShader(frag)
            except Exception:
                pass
            vert = None
            frag = None
            prog = None
            continue
    if prog is None:
        if last_exc is not None:
            raise last_exc
        raise RuntimeError('Failed to compile any shader variant')

    try:
        presenter._fs_prog = int(prog)
        loc_tex = gl.glGetUniformLocation(prog, b'u_tex')
        loc_flip = gl.glGetUniformLocation(prog, b'u_flip_y')
        presenter._fs_prog_u_tex = int(loc_tex) if loc_tex is not None else None
        presenter._fs_prog_u_flip = int(loc_flip) if loc_flip is not None else None
        presenter._fs_prog_attrib_pos = 0
        presenter._fs_prog_attrib_uv = 1
    except Exception:
        presenter._fs_prog = None
        raise

    import array
    verts = array.array('f', [
        -1.0, -1.0, 0.0, 0.0,
         1.0, -1.0, 1.0, 0.0,
         1.0,  1.0, 1.0, 1.0,
        -1.0, -1.0, 0.0, 0.0,
         1.0,  1.0, 1.0, 1.0,
        -1.0,  1.0, 0.0, 1.0,
    ])

    vbo = gl.GLuint()
    gl.glGenBuffers(1, ctypes.byref(vbo))
    presenter._fs_vbo = int(vbo.value)
    try:
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, int(presenter._fs_vbo))
        size = ctypes.sizeof(ctypes.c_float) * len(verts)
        ptr = (ctypes.c_float * len(verts))(*verts)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, size, ctypes.byref(ptr), gl.GL_STATIC_DRAW)
    finally:
        try:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        except Exception:
            pass

    try:
        if hasattr(gl, 'glGenVertexArrays') and hasattr(gl, 'glBindVertexArray'):
            vao = gl.GLuint()
            gl.glGenVertexArrays(1, ctypes.byref(vao))
            presenter._fs_vao = int(vao.value)
            try:
                gl.glBindVertexArray(int(presenter._fs_vao))
                gl.glBindBuffer(gl.GL_ARRAY_BUFFER, int(presenter._fs_vbo))
                stride = ctypes.sizeof(ctypes.c_float) * 4
                try:
                    gl.glEnableVertexAttribArray(presenter._fs_prog_attrib_pos)
                    gl.glVertexAttribPointer(presenter._fs_prog_attrib_pos, 2, gl.GL_FLOAT, False, stride, ctypes.c_void_p(0))
                    gl.glEnableVertexAttribArray(presenter._fs_prog_attrib_uv)
                    gl.glVertexAttribPointer(presenter._fs_prog_attrib_uv, 2, gl.GL_FLOAT, False, stride, ctypes.c_void_p(ctypes.sizeof(ctypes.c_float) * 2))
                except Exception:
                    pass
            finally:
                try:
                    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
                except Exception:
                    pass
                try:
                    gl.glBindVertexArray(0)
                except Exception:
                    pass
    except Exception:
        try:
            presenter._fs_vao = None
        except Exception:
            pass

    try:
        logging.getLogger(__name__).debug('VBO created prog=%r vbo=%r vao=%r', presenter._fs_prog, presenter._fs_vbo, presenter._fs_vao)
    except Exception:
        pass
    try:
        err = int(gl.glGetError())
        if err != 0:
            logging.getLogger(__name__).debug('VBO glGetError after resource create: %r', err)
    except Exception:
        pass


def _draw_textured_quad_vbo(presenter: Any, tex_id: int, flip_y: bool = True):
    from pyglet import gl
    if not getattr(presenter, '_fs_prog', None) or not getattr(presenter, '_fs_vbo', None):
        raise RuntimeError('Textured-quad resources not initialized')

    prog = int(presenter._fs_prog)
    prev_prog = gl.GLint()
    try:
        gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM, ctypes.byref(prev_prog))
    except Exception:
        prev_prog = None

    gl.glUseProgram(prog)
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, int(tex_id))
    try:
        if presenter._fs_prog_u_tex is not None:
            gl.glUniform1i(presenter._fs_prog_u_tex, 0)
        if presenter._fs_prog_u_flip is not None:
            gl.glUniform1f(presenter._fs_prog_u_flip, 1.0 if flip_y else 0.0)
    except Exception:
        pass

    bound_vao = False
    try:
        if getattr(presenter, '_fs_vao', None) is not None:
            try:
                gl.glBindVertexArray(int(presenter._fs_vao))
                bound_vao = True
            except Exception:
                bound_vao = False
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, int(presenter._fs_vbo))
            stride = ctypes.sizeof(ctypes.c_float) * 4
            try:
                gl.glEnableVertexAttribArray(presenter._fs_prog_attrib_pos)
                gl.glVertexAttribPointer(presenter._fs_prog_attrib_pos, 2, gl.GL_FLOAT, False, stride, ctypes.c_void_p(0))
                gl.glEnableVertexAttribArray(presenter._fs_prog_attrib_uv)
                gl.glVertexAttribPointer(presenter._fs_prog_attrib_uv, 2, gl.GL_FLOAT, False, stride, ctypes.c_void_p(ctypes.sizeof(ctypes.c_float) * 2))
            except Exception:
                pass
    except Exception:
        pass

    try:
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFuncSeparate(gl.GL_ONE, gl.GL_ONE_MINUS_SRC_ALPHA, gl.GL_ONE, gl.GL_ONE_MINUS_SRC_ALPHA)
    except Exception:
        pass

    try:
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
    except Exception:
        try:
            err = int(gl.glGetError())
            logging.getLogger(__name__).debug('VBO glDrawArrays raised, glGetError=%r', err)
        except Exception:
            pass
        raise

    try:
        err = int(gl.glGetError())
        if err != 0:
            logging.getLogger(__name__).debug('VBO glDrawArrays completed but glGetError=%r', err)
    except Exception:
        pass

    try:
        if bound_vao:
            try:
                gl.glBindVertexArray(0)
            except Exception:
                pass
        else:
            try:
                gl.glDisableVertexAttribArray(presenter._fs_prog_attrib_pos)
                gl.glDisableVertexAttribArray(presenter._fs_prog_attrib_uv)
            except Exception:
                pass
            try:
                gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
            except Exception:
                pass
    except Exception:
        pass
    try:
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    except Exception:
        pass
    try:
        if prev_prog is not None:
            gl.glUseProgram(int(prev_prog))
        else:
            gl.glUseProgram(0)
    except Exception:
        pass
