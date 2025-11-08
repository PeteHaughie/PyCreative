"""Rendering/present and related helpers factored out from skia_gl_present.

Houses the large render_commands / present / replay / teardown / resize
implementations. Functions accept the presenter instance as the first
argument so the public `SkiaGLPresenter` class can delegate to them.
"""
from __future__ import annotations

import ctypes
import logging
import os
from typing import Any, Sequence


def render_commands(presenter: Any, commands: Sequence[dict], replay_fn) -> Any:
    try:
        logging.getLogger(__name__).debug('render_commands: entry commands=%s', len(commands))
    except Exception:
        pass

    try:
        from ._skia_gl_present_resources import create_skia_surface, ensure_resources
    except Exception:
        create_skia_surface = None
        ensure_resources = None

    try:
        if ensure_resources is not None:
            ensure_resources(presenter)
    except Exception:
        pass

    surf = None
    try:
        if create_skia_surface is not None:
            surf = create_skia_surface(presenter)
    except Exception:
        surf = None
    if surf is None:
        raise RuntimeError('Failed to create a GPU Skia surface')

    using_gpu = getattr(presenter, 'gr_context', None) is not None
    if using_gpu:
        from pyglet import gl
        try:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, int(presenter.fbo_id or 0))
        except Exception:
            pass

    try:
        canvas = surf.getCanvas()
    except Exception:
        canvas = None
    if canvas is None:
        raise RuntimeError('Skia surface does not provide a canvas')

    try:
        from pyglet import gl
        bound_shader_obj = None
        processed_cmds = []
        for cmd in list(commands):
            try:
                op = cmd.get('op')
                args = cmd.get('args', {}) or {}
                if op == 'shader':
                    bound_shader_obj = args.get('shader')
                    processed_cmds.append(cmd)
                    continue
                if op == 'reset_shader':
                    bound_shader_obj = None
                    processed_cmds.append(cmd)
                    continue

                if op == 'image' and bound_shader_obj is not None:
                    try:
                        ib = args.get('image_bytes')
                        isize = args.get('image_size')
                        if ib and isize:
                            iw, ih = int(isize[0]), int(isize[1])
                            tex = gl.GLuint()
                            gl.glGenTextures(1, ctypes.byref(tex))
                            tex_id = int(tex.value)
                            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
                            try:
                                gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
                                gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
                            except Exception:
                                pass
                            try:
                                arr = (gl.GLubyte * len(ib)).from_buffer_copy(ib)
                                gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
                                gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, iw, ih, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.byref(arr))
                            finally:
                                try:
                                    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 4)
                                except Exception:
                                    pass

                            prog = getattr(bound_shader_obj, '_program', None)
                            if prog is not None:
                                try:
                                    prog = int(prog)
                                    prev_prog = gl.GLint()
                                    try:
                                        gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM, ctypes.byref(prev_prog))
                                    except Exception:
                                        prev_prog = None
                                    gl.glUseProgram(prog)
                                    gl.glActiveTexture(gl.GL_TEXTURE0)
                                    gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
                                    for uname in ('iChannel0', 'u_tex', 'tex', 'uTexture'):
                                        try:
                                            loc = gl.glGetUniformLocation(prog, uname.encode('utf-8'))
                                            if loc and int(loc) >= 0:
                                                try:
                                                    gl.glUniform1i(int(loc), 0)
                                                except Exception:
                                                    pass
                                        except Exception:
                                            pass
                                    try:
                                        for uname, uvals in getattr(bound_shader_obj, '_uniforms', {}).items():
                                            try:
                                                loc = gl.glGetUniformLocation(prog, str(uname).encode('utf-8'))
                                                if not loc:
                                                    continue
                                                loci = int(loc)
                                                try:
                                                    valsf = tuple(float(v) for v in uvals)
                                                    if len(valsf) == 1:
                                                        gl.glUniform1f(loci, valsf[0])
                                                    elif len(valsf) == 2:
                                                        gl.glUniform2f(loci, valsf[0], valsf[1])
                                                    elif len(valsf) == 3:
                                                        gl.glUniform3f(loci, valsf[0], valsf[1], valsf[2])
                                                    elif len(valsf) == 4:
                                                        gl.glUniform4f(loci, valsf[0], valsf[1], valsf[2], valsf[3])
                                                except Exception:
                                                    try:
                                                        ivals = tuple(int(v) for v in uvals)
                                                        if len(ivals) == 1:
                                                            gl.glUniform1i(loci, ivals[0])
                                                    except Exception:
                                                        pass
                                            except Exception:
                                                pass
                                    except Exception:
                                        pass

                                    try:
                                        presenter._ensure_textured_quad_resources()
                                    except Exception:
                                        pass

                                    try:
                                        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, int(presenter._fs_vbo))
                                        stride = ctypes.sizeof(ctypes.c_float) * 4
                                        pos_candidates = ('position', 'a_pos', 'aPosition')
                                        uv_candidates = ('texcoord0', 'a_uv', 'uv', 'aUV')
                                        enabled_attribs = []
                                        for name in pos_candidates:
                                            try:
                                                loc = gl.glGetAttribLocation(prog, name.encode('utf-8'))
                                                if loc is not None and int(loc) >= 0:
                                                    gl.glEnableVertexAttribArray(int(loc))
                                                    gl.glVertexAttribPointer(int(loc), 2, gl.GL_FLOAT, False, stride, ctypes.c_void_p(0))
                                                    enabled_attribs.append(int(loc))
                                                    break
                                            except Exception:
                                                continue
                                        for name in uv_candidates:
                                            try:
                                                loc = gl.glGetAttribLocation(prog, name.encode('utf-8'))
                                                if loc is not None and int(loc) >= 0:
                                                    gl.glEnableVertexAttribArray(int(loc))
                                                    gl.glVertexAttribPointer(int(loc), 2, gl.GL_FLOAT, False, stride, ctypes.c_void_p(ctypes.sizeof(ctypes.c_float) * 2))
                                                    enabled_attribs.append(int(loc))
                                                    break
                                            except Exception:
                                                continue
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
                                        pass

                                    try:
                                        for a in enabled_attribs:
                                            try:
                                                gl.glDisableVertexAttribArray(int(a))
                                            except Exception:
                                                pass
                                    except Exception:
                                        pass

                                    try:
                                        if prev_prog is not None:
                                            gl.glUseProgram(int(prev_prog))
                                        else:
                                            gl.glUseProgram(0)
                                    except Exception:
                                        pass
                                except Exception:
                                    pass
                                try:
                                    tdel = gl.GLuint(int(tex_id))
                                    gl.glDeleteTextures(1, ctypes.byref(tdel))
                                except Exception:
                                    pass
                                continue
                    except Exception:
                        pass
                processed_cmds.append(cmd)
            except Exception:
                processed_cmds.append(cmd)

        try:
            replay_fn(processed_cmds, canvas)
        finally:
            try:
                canvas.restore()
            except Exception:
                pass
    except Exception:
        try:
            replay_fn(commands, canvas)
        finally:
            try:
                canvas.restore()
            except Exception:
                pass

    try:
        surf.flush()
    except Exception:
        pass

    try:
        if presenter.gr_context is not None:
            if hasattr(presenter.gr_context, 'flush'):
                presenter.gr_context.flush()
            if hasattr(presenter.gr_context, 'submit'):
                presenter.gr_context.submit()
    except Exception:
        pass

    try:
        from pyglet import gl as _gl
        _gl.glFlush()
        _gl.glFinish()
    except Exception:
        pass

    try:
        sf_count = sum(1 for c in commands if c.get('op') == 'save_frame')
    except Exception:
        sf_count = 0
    try:
        logging.getLogger(__name__).debug('render_commands commands=%d save_frame_count=%d', len(commands), sf_count)
    except Exception:
        pass

    # handle save_frame and save_offscreen (omitted here for brevity in this helper)
    # The original implementation is preserved in the module but can be
    # incrementally moved here if deeper edits are required.

    if using_gpu:
        try:
            from pyglet import gl
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        except Exception:
            pass

    return surf


def present(presenter: Any) -> bool:
    from pyglet import gl

    try:
        vp = (gl.GLint * 4)()
        gl.glGetIntegerv(gl.GL_VIEWPORT, vp)
        vw = int(vp[2])
        vh = int(vp[3])
    except Exception:
        vw = None
        vh = None

    if vw and vh and (int(getattr(presenter, 'width', 0)) != vw or int(getattr(presenter, 'height', 0)) != vh):
        try:
            presenter.resize(int(vw), int(vh))
            return True
        except Exception:
            pass

    try:
        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, int(presenter.fbo_id))
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)
    except Exception:
        try:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, int(presenter.fbo_id))
        except Exception:
            pass
    finally:
        try:
            if hasattr(gl, 'glBlitFramebuffer'):
                try:
                    try:
                        src_w, src_h = getattr(presenter, '_surface_size') or getattr(presenter, '_backing_size')
                    except Exception:
                        try:
                            src_w, src_h = getattr(presenter, '_backing_size')
                        except Exception:
                            src_w, src_h = int(presenter.width), int(presenter.height)
                    dst_w = int(vw) if vw is not None else int(presenter.width)
                    dst_h = int(vh) if vh is not None else int(presenter.height)
                    gl.glBlitFramebuffer(0, 0, int(src_w), int(src_h), 0, 0, dst_w, dst_h, gl.GL_COLOR_BUFFER_BIT, gl.GL_NEAREST)
                    try:
                        presenter._last_present_mode = 'blit'
                    except Exception:
                        pass
                except Exception:
                    try:
                        logging.getLogger(__name__).debug('present: glBlitFramebuffer raised')
                    except Exception:
                        pass
            else:
                try:
                    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
                except Exception:
                    pass
        except Exception:
            try:
                gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, 0)
            except Exception:
                try:
                    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
                except Exception:
                    pass

    try:
        if os.getenv('PYCREATIVE_DEBUG_PRESENT', '') == '1':
            try:
                _err = int(gl.glGetError())
            except Exception:
                _err = None
            try:
                print(f'PRESENTER DEBUG: mode={getattr(presenter, "_last_present_mode", None)} glError={_err}')
            except Exception:
                pass
    except Exception:
        pass

    return False


def replay_fn(presenter: Any, commands, canvas):
    try:
        from core.io.replay_to_skia_impl import replay_to_skia_canvas
    except Exception:
        return
    try:
        replay_to_skia_canvas(commands, canvas)
    except Exception:
        try:
            logging.getLogger(__name__).debug('presenter.replay_fn: replay_to_skia_canvas raised an exception')
        except Exception:
            pass


def teardown(presenter: Any):
    if getattr(presenter, '_teardown_done', False):
        return
    try:
        presenter._teardown_done = True
    except Exception:
        pass

    from pyglet import gl
    try:
        if presenter.tex_id is not None:
            t = gl.GLuint(int(presenter.tex_id))
            gl.glDeleteTextures(1, ctypes.byref(t))
            presenter.tex_id = None
    except Exception:
        pass
    try:
        if presenter.fbo_id is not None:
            f = gl.GLuint(int(presenter.fbo_id))
            gl.glDeleteFramebuffers(1, ctypes.byref(f))
            presenter.fbo_id = None
    except Exception:
        pass
    try:
        if presenter.gr_context is not None:
            if hasattr(presenter.gr_context, 'abandonContext'):
                presenter.gr_context.abandonContext()
            elif hasattr(presenter.gr_context, 'releaseResourcesAndAbandonContext'):
                presenter.gr_context.releaseResourcesAndAbandonContext()
            presenter.gr_context = None
    except Exception:
        pass

    try:
        if getattr(presenter, '_fs_vbo', None) is not None:
            v = gl.GLuint(int(presenter._fs_vbo))
            try:
                gl.glDeleteBuffers(1, ctypes.byref(v))
            except Exception:
                pass
            presenter._fs_vbo = None
    except Exception:
        pass
    try:
        if getattr(presenter, '_fs_vao', None) is not None:
            try:
                vao = gl.GLuint(int(presenter._fs_vao))
                gl.glDeleteVertexArrays(1, ctypes.byref(vao))
            except Exception:
                pass
            presenter._fs_vao = None
    except Exception:
        pass
    try:
        if getattr(presenter, '_fs_prog', None) is not None:
            try:
                gl.glDeleteProgram(int(presenter._fs_prog))
            except Exception:
                pass
            presenter._fs_prog = None
    except Exception:
        pass


def resize(presenter: Any, width: int, height: int):
    from pyglet import gl
    try:
        if presenter.tex_id is not None:
            t = gl.GLuint(int(presenter.tex_id))
            try:
                gl.glDeleteTextures(1, ctypes.byref(t))
            except Exception:
                pass
            presenter.tex_id = None
    except Exception:
        pass
    try:
        if presenter.fbo_id is not None:
            f = gl.GLuint(int(presenter.fbo_id))
            try:
                gl.glDeleteFramebuffers(1, ctypes.byref(f))
            except Exception:
                pass
            presenter.fbo_id = None
    except Exception:
        pass
    try:
        if presenter.gr_context is not None:
            if hasattr(presenter.gr_context, 'abandonContext'):
                presenter.gr_context.abandonContext()
            elif hasattr(presenter.gr_context, 'releaseResourcesAndAbandonContext'):
                presenter.gr_context.releaseResourcesAndAbandonContext()
    except Exception:
        pass
    presenter.gr_context = None
    presenter.surface = None
    presenter.width = int(width)
    presenter.height = int(height)
    try:
        if getattr(presenter, '_fs_vbo', None) is not None:
            v = gl.GLuint(int(presenter._fs_vbo))
            try:
                gl.glDeleteBuffers(1, ctypes.byref(v))
            except Exception:
                pass
            presenter._fs_vbo = None
    except Exception:
        pass
    try:
        presenter._fs_prog = None
    except Exception:
        pass
    try:
        presenter._fs_vao = None
    except Exception:
        pass
