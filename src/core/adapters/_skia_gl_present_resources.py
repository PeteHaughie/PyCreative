"""Resource allocation and Skia surface creation factored out from skia_gl_present.

These functions accept a presenter instance as the first argument and
perform the original behaviors previously implemented as methods.
"""
from __future__ import annotations

import ctypes
import logging
import time
from typing import Any


def ensure_resources(presenter: Any):
    from pyglet import gl

    if presenter.tex_id is None:
        tex = gl.GLuint()
        gl.glGenTextures(1, ctypes.byref(tex))
        presenter.tex_id = int(tex.value)
        gl.glBindTexture(gl.GL_TEXTURE_2D, presenter.tex_id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        bw = bh = None
        try:
            if getattr(presenter, '_window', None) is not None:
                try:
                    fb = getattr(presenter._window, 'get_framebuffer_size', None)
                    if fb is not None:
                        fw, fh = presenter._window.get_framebuffer_size()
                        if fw and fh:
                            bw, bh = int(fw), int(fh)
                    else:
                        pr = getattr(presenter._window, 'get_pixel_ratio', None)
                        if pr is not None:
                            ratio = float(presenter._window.get_pixel_ratio())
                            if ratio and ratio != 1.0:
                                bw = int(presenter.width * ratio)
                                bh = int(presenter.height * ratio)
                except Exception:
                    bw = bh = None
        except Exception:
            bw = bh = None

        if bw is None or bh is None:
            try:
                vp = (gl.GLint * 4)()
                gl.glGetIntegerv(gl.GL_VIEWPORT, vp)
                bw = int(vp[2])
                bh = int(vp[3])
                if bw <= 0 or bh <= 0:
                    raise Exception('invalid viewport')
            except Exception:
                bw = int(presenter.width)
                bh = int(presenter.height)

        try:
            internal = gl.GL_RGBA8
        except Exception:
            internal = gl.GL_RGBA

        try:
            presenter._backing_size = (int(bw), int(bh))
        except Exception:
            pass

        try:
            logging.getLogger(__name__).debug('ensure_resources: allocating GL texture tex_id=%s size=%s', presenter.tex_id, (int(bw), int(bh)))
        except Exception:
            pass
        try:
            with open('/tmp/pycreative_present_allocations.log', 'a') as _af:
                _af.write(f'{time.time():.6f} ensure_resources: tex_id={presenter.tex_id} alloc_w={int(bw)} alloc_h={int(bh)}\n')
        except Exception:
            pass

        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, internal, bw, bh, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)

        try:
            bg = getattr(presenter, '_setup_background_color', None)
            if bg is not None:
                try:
                    r = int(bg[0]) & 0xFF
                    g = int(bg[1]) & 0xFF
                    b = int(bg[2]) & 0xFF
                    w = int(presenter.width)
                    h = int(presenter.height)
                    buf_len = w * h * 4
                    arr_type = (gl.GLubyte * buf_len)
                    buf = arr_type()
                    idx = 0
                    for _ in range(w * h):
                        buf[idx] = r
                        buf[idx + 1] = g
                        buf[idx + 2] = b
                        buf[idx + 3] = 255
                        idx += 4
                    try:
                        try:
                            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
                        except Exception:
                            pass
                        try:
                            gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, w, h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, buf)
                        except Exception:
                            try:
                                gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, w, h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.byref(buf))
                            except Exception:
                                pass
                    finally:
                        try:
                            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 4)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    if presenter.fbo_id is None:
        fbo = gl.GLuint()
        gl.glGenFramebuffers(1, ctypes.byref(fbo))
        presenter.fbo_id = int(fbo.value)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, int(presenter.fbo_id))
        try:
            bw, bh = getattr(presenter, '_backing_size')
        except Exception:
            bw, bh = int(presenter.width), int(presenter.height)
        if bw and bh:
            try:
                gl.glViewport(0, 0, int(bw), int(bh))
            except Exception:
                pass
        try:
            gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, int(presenter.tex_id), 0)
        except Exception:
            try:
                gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, int(presenter.tex_id), 0)
            except Exception:
                pass
        try:
            status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
            if status != gl.GL_FRAMEBUFFER_COMPLETE:
                print('SkiaGLPresenter: FBO incomplete status=', status)
        except Exception:
            pass
        try:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        except Exception:
            pass


def create_skia_surface(presenter: Any):
    try:
        import skia
    except Exception:
        return None

    try:
        ensure_resources(presenter)
    except Exception:
        pass

    try:
        current_backing = getattr(presenter, '_backing_size')
    except Exception:
        current_backing = (int(presenter.width), int(presenter.height))
    if getattr(presenter, 'surface', None) is not None and getattr(presenter, 'gr_context', None) is not None and presenter._surface_size == (int(current_backing[0]), int(current_backing[1])):
        try:
            logging.getLogger(__name__).debug('create_skia_surface: reusing existing GPU surface')
        except Exception:
            pass
        return presenter.surface

    ctx = skia.GrDirectContext.MakeGL()
    if ctx is None:
        try:
            logging.getLogger(__name__).debug('create_skia_surface: GrDirectContext.MakeGL() returned None')
        except Exception:
            pass
        return None

    from pyglet import gl

    try:
        fb_fmt = int(gl.GL_RGBA8)
    except Exception:
        fb_fmt = int(gl.GL_RGBA)

    try:
        bw, bh = getattr(presenter, '_backing_size')
    except Exception:
        bw, bh = int(presenter.width), int(presenter.height)

    try:
        logging.getLogger(__name__).debug('create_skia_surface: creating backend RT fbo=%s tex=%s size=%s', presenter.fbo_id, presenter.tex_id, (int(bw), int(bh)))
    except Exception:
        pass
    try:
        with open('/tmp/pycreative_present_allocations.log', 'a') as _af:
            _af.write(f'create_skia_surface: fbo={presenter.fbo_id} tex={presenter.tex_id} rt_w={int(bw)} rt_h={int(bh)}\n')
    except Exception:
        pass

    fb_info = skia.GrGLFramebufferInfo(int(presenter.fbo_id or 0), fb_fmt)
    backend_rt = skia.GrBackendRenderTarget(int(bw), int(bh), 0, 0, fb_info)
    surf = skia.Surface.MakeFromBackendRenderTarget(
        ctx,
        backend_rt,
        skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType,
        skia.ColorSpace.MakeSRGB(),
    )
    if surf is None:
        try:
            logging.getLogger(__name__).debug('create_skia_surface: MakeFromBackendRenderTarget returned None')
        except Exception:
            pass
        return None

    presenter.gr_context = ctx
    presenter.surface = surf
    try:
        try:
            bw, bh = getattr(presenter, '_backing_size', (int(presenter.width), int(presenter.height)))
        except Exception:
            bw, bh = int(presenter.width), int(presenter.height)
        presenter._surface_size = (int(bw), int(bh))
        try:
            presenter._backing_size = (int(bw), int(bh))
        except Exception:
            pass
    except Exception:
        presenter._surface_size = None
    try:
        logging.getLogger(__name__).debug('create_skia_surface: created GPU surface fbo=%s tex=%s size=%s %s', presenter.fbo_id, presenter.tex_id, presenter.width, presenter.height)
    except Exception:
        pass
    return surf
