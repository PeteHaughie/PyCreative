"""GPU-backed Skia adapter scaffold.

This module attempts to provide an adapter that creates GPU-backed Skia
surfaces (OpenGL/Metal/Vulkan) and presents them in a way that allows
zero-copy or efficient texture sharing with the display system.

from src.core.debug import debug
The implementation here is intentionally conservative: it guards against
skia-python not being installed and exposes a CPU fallback when GPU
support can't be initialised. Detailed GPU interop is platform-specific
and may require SDL/pygame to be initialised with an OpenGL/Metal
context and skia-python built with the corresponding GPU backend.

Public API (adapter):
- register_api(engine) -> registers self as engine._graphics_adapter
- create_gpu_surface(width, height) -> attempts to create a GPU-backed
  Skia surface; may return None on failure.
- present(skia_surface, target_display_surface) -> present surface to the
  display; may be a no-op if GPU interop isn't available.

This scaffold provides safe defaults so tests and CI remain stable.
"""
from typing import Any, Optional
from src.core.debug import debug

# Optional heavy imports
_skia = None
try:
    import skia as _skia
except Exception:
    _skia = None

# Import pygame lazily in functions to avoid test-time side effects


class SkiaGPUAdapter:
    """Adapter that exposes a GPU-backed Skia surface API where possible.

    The methods below are intentionally conservative and should be safe to
    import on systems without skia-python or without GPU support.
    """

    def register_api(self, engine: Any) -> None:
        engine._graphics_adapter = self

    def create_gpu_surface(self, width: int, height: int) -> Optional[Any]:
        """Attempt to create and return a GPU-backed Skia surface.

        Returns None if skia isn't available or GPU context creation fails.
        """
        if _skia is None:
            debug("skia not available in skia_gpu_adapter.create_gpu_surface")
            return None

        # Try to create a GL-backed GrDirectContext. The exact API names in
        # skia-python may vary by version; guard each call. If any step fails
        # return None so callers will fall back to CPU surfaces.
        try:
            # Prefer GrDirectContext creation helpers if present
            GrDirectContext = getattr(_skia, "GrDirectContext", None)
            if GrDirectContext is None:
                debug("GrDirectContext not found on skia; cannot create GPU context")
                return None

            # Attempt to make a GL context-driven GrDirectContext. Many
            # skia-python builds expose `MakeGL` or `Make` helpers; try a few
            # common variants.
            ctx = None
            if hasattr(GrDirectContext, "MakeGL"):
                try:
                    ctx = GrDirectContext.MakeGL()
                except Exception:
                    ctx = None
            elif hasattr(GrDirectContext, "Make"):
                # Some builds expose a generic Make() that accepts a backend.
                try:
                    ctx = GrDirectContext.Make()
                except Exception:
                    ctx = None

            if ctx is None:
                debug("Failed to create GrDirectContext (ctx is None)")
                return None

            # Create a render target surface bound to the current GL context.
            ColorType = getattr(_skia, "ColorType", None)
            AlphaType = getattr(_skia, "AlphaType", None)
            if ColorType is None or AlphaType is None:
                return None

            info = _skia.ImageInfo.Make(width, height,
                                         ColorType.kRGBA_8888_ColorType,
                                         AlphaType.kPremul_AlphaType)

            # Use MakeRenderTarget or MakeOnScreen depending on availability
            surface = None
            if hasattr(_skia.Surface, "MakeRenderTarget"):
                try:
                    surface = _skia.Surface.MakeRenderTarget(ctx, _skia.Budgeted.kNo, info)
                except Exception:
                    surface = None

            # If we couldn't create an offscreen render target, try a generic
            # MakeOnScreen (some bindings expose this to wrap the default FB).
            if surface is None and hasattr(_skia.Surface, "MakeOnScreen"):
                try:
                    surface = _skia.Surface.MakeOnScreen(ctx, info)
                except Exception:
                    surface = None

            if surface is None:
                debug("Failed to create GPU Skia surface (surface is None)")
            else:
                try:
                    sw = getattr(surface, 'width', lambda: None)()
                    sh = getattr(surface, 'height', lambda: None)()
                    debug(f"Created GPU Skia surface: {surface} size=({sw},{sh})")
                except Exception:
                    debug(f"Created GPU Skia surface: {surface}")

            return surface
        except Exception as exc:
            debug(f"Exception while attempting to create GPU Skia surface: {exc}")
            return None

    def present(self, skia_surface: Any, target_display_surface: Any) -> None:
        """Present the skia_surface.

        If true GPU interop is available, this should perform a zero-copy
        texture transfer or texture bind to the display surface's GL/Metal
        context. Here we provide a conservative default: if the surface has a
        `flushAndSubmit` or `flush` API, call it; otherwise do nothing.
        """
        debug(f"skia_gpu_adapter.present called; target_display_surface={type(target_display_surface)}")

        if skia_surface is None:
            return

        # If we have a GPU-backed Skia surface, try to present it via GL.
        # This code is conservative: it checks for attributes that some
        # skia-python builds expose (e.g., `getBackendTexture` / `getTextureInfo`)
        # and falls back to flushing if nothing suitable is found.
        try:
            # Some surfaces expose a method to get a backend texture handle.
            # The exact API varies; try several known variants.
            tex = None
            if hasattr(skia_surface, "getBackendTexture"):
                try:
                    tex = skia_surface.getBackendTexture()
                except Exception:
                    tex = None
            elif hasattr(skia_surface, "getTextureInfo"):
                try:
                    tex = skia_surface.getTextureInfo()
                except Exception:
                    tex = None

            # If we obtained a GL texture handle, perform a minimal GL bind+
            # blit to the default framebuffer. This requires PyOpenGL or ctypes
            # bindings; avoid hard dependency by guarding it.
            if tex is not None:
                debug(f"getBackendTexture/getTextureInfo returned: {tex}")
                try:
                    # tex may be a simple integer handle or an object with `handle`.
                    handle = tex if isinstance(tex, int) else getattr(tex, 'handle', None)
                    if handle is None:
                        debug("No direct 'handle' on tex; trying fID/id attributes")
                        # Try common attribute names
                        handle = getattr(tex, 'fID', None) or getattr(tex, 'id', None)

                    if handle is not None:
                        debug(f"Extracted GL handle: {handle}")
                        # Prefer a PyOpenGL path if available; otherwise try the
                        # conservative ctypes textured-quad blit helper.
                        tried_gl = False
                        try:
                            from OpenGL import GL
                            tried_gl = True
                            debug("Using PyOpenGL path for present()")
                            GL.glBindTexture(GL.GL_TEXTURE_2D, handle)
                            # Caller must ensure the Skia surface is flushed
                            if hasattr(skia_surface, 'flushAndSubmit'):
                                skia_surface.flushAndSubmit()
                            elif hasattr(skia_surface, 'flush'):
                                skia_surface.flush()
                            # If a target display surface is provided and has a
                            # present function, call it (pygame.display.flip())
                            if target_display_surface is not None:
                                try:
                                    # target_display_surface is typically a
                                    # pygame surface module; call its present
                                    # function if available.
                                    present_fn = getattr(target_display_surface, 'present', None)
                                    if callable(present_fn):
                                        present_fn()
                                except Exception:
                                    try:
                                        import pygame as _pg
                                        _pg.display.flip()
                                    except Exception:
                                        pass
                        except Exception as exc:
                            debug(f"PyOpenGL present-path failed: {exc}")
                            # Fallback path: use ctypes blit helper
                            try:
                                # Determine width/height when available
                                w, h = getattr(target_display_surface, 'get_size', lambda: (None, None))()
                                if w is None or h is None:
                                    # Try to infer from skia surface if possible
                                    try:
                                        w = skia_surface.width()
                                        h = skia_surface.height()
                                    except Exception:
                                        w, h = 640, 480
                                debug("Falling back to ctypes GL blit helper")
                                _blit_texture_ctypes(handle, w, h)
                                # Finally, swap buffers (pygame flip) if possible
                                try:
                                    import pygame as _pg
                                    _pg.display.flip()
                                except Exception:
                                    pass
                            except Exception as exc:
                                debug(f"ctypes blit helper failed: {exc}")
                                # If blit failed, fall back to flush
                                if hasattr(skia_surface, 'flushAndSubmit'):
                                    skia_surface.flushAndSubmit()
                                elif hasattr(skia_surface, 'flush'):
                                    skia_surface.flush()
                    else:
                        debug("No usable GL handle extracted from backend texture; flushing")
                        # No usable handle; flush as a fallback.
                        if hasattr(skia_surface, 'flushAndSubmit'):
                            skia_surface.flushAndSubmit()
                        elif hasattr(skia_surface, 'flush'):
                            skia_surface.flush()
                except Exception:
                    # Any errors during GL path: fallback to flush
                    if hasattr(skia_surface, 'flushAndSubmit'):
                        skia_surface.flushAndSubmit()
                    elif hasattr(skia_surface, 'flush'):
                        skia_surface.flush()
            else:
                # No backend texture available: perform a flush to ensure
                # Skia completes pending draws. The display adapter should
                # perform buffer swap (e.g., pygame.display.flip()).
                if hasattr(skia_surface, 'flushAndSubmit'):
                    skia_surface.flushAndSubmit()
                elif hasattr(skia_surface, 'flush'):
                    skia_surface.flush()
        except Exception:
            # No-op fallback; preserve test/CI stability.
            try:
                if hasattr(skia_surface, 'flush'):
                    skia_surface.flush()
            except Exception:
                pass


# Export a module-level instance for convenience
skia_gpu_adapter = SkiaGPUAdapter()


# Backwards-compatible names the rest of the codebase may expect
def register_api(engine: Any) -> None:  # pragma: no cover - tiny shim
    skia_gpu_adapter.register_api(engine)


__all__ = ["SkiaGPUAdapter", "skia_gpu_adapter", "register_api"]

# Minimal ctypes-based GL helpers (used only when PyOpenGL isn't present).
_gl = None
_have_gl_funcs = False
_gl_program = 0
_gl_vao = 0
_gl_vbo = 0
_gl_blit_ready = False


def _load_gl_lib():
    """Attempt to load a system GL library via ctypes.

    Returns a CDLL or None.
    """
    global _gl
    if _gl is not None:
        return _gl
    import ctypes
    from ctypes.util import find_library

    names = [
        find_library('GL'),
        find_library('OpenGL'),
        'libGL.so.1',
        '/System/Library/Frameworks/OpenGL.framework/OpenGL'
    ]
    for name in names:
        if not name:
            continue
        try:
            _gl = ctypes.CDLL(name)
            return _gl
        except Exception:
            continue
    _gl = None
    return None


def _debug(msg: str) -> None:
    try:
        import os
        if os.environ.get('PYCREATIVE_DEBUG', '') == '1':
            print(f"[skia_gpu_adapter] {msg}")
    except Exception:
        pass


def _ensure_gl_funcs():
    """Ensure basic GL functions are available via ctypes.

    This loads a small set of legacy immediate-mode functions used as a
    conservative fallback for textured blits. Return True if available.
    """
    global _have_gl_funcs
    if _have_gl_funcs:
        return True
    gl = _load_gl_lib()
    if gl is None:
        return False
    import ctypes

    try:
        # Bind required functions
        gl.glEnable.argtypes = [ctypes.c_uint]
        gl.glEnable.restype = None
        gl.glDisable.argtypes = [ctypes.c_uint]
        gl.glDisable.restype = None
        gl.glBindTexture.argtypes = [ctypes.c_uint, ctypes.c_uint]
        gl.glBindTexture.restype = None
        gl.glBegin.argtypes = [ctypes.c_uint]
        gl.glBegin.restype = None
        gl.glEnd.argtypes = []
        gl.glEnd.restype = None
        gl.glTexCoord2f.argtypes = [ctypes.c_float, ctypes.c_float]
        gl.glTexCoord2f.restype = None
        gl.glVertex2f.argtypes = [ctypes.c_float, ctypes.c_float]
        gl.glVertex2f.restype = None
        gl.glFlush.argtypes = []
        gl.glFlush.restype = None

        # Matrix / projection helpers
        gl.glMatrixMode.argtypes = [ctypes.c_uint]
        gl.glMatrixMode.restype = None
        gl.glPushMatrix.argtypes = []
        gl.glPushMatrix.restype = None
        gl.glPopMatrix.argtypes = []
        gl.glPopMatrix.restype = None
        gl.glLoadIdentity.argtypes = []
        gl.glLoadIdentity.restype = None
        # glOrtho and glViewport signatures
        gl.glOrtho.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
        gl.glOrtho.restype = None
        gl.glViewport.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        gl.glViewport.restype = None
    except Exception:
        return False

    _have_gl_funcs = True
    return True


def _blit_texture_ctypes(handle: int, w: int, h: int) -> None:
    """Draw a fullscreen textured quad using legacy GL calls via ctypes.

    This is intentionally minimal and uses the fixed-function pipeline. It
    serves as a conservative fallback when shaders/VAOs aren't available.
    """
    gl = _load_gl_lib()
    if gl is None:
        return
    try:
        ctypes = __import__('ctypes')
        # Ensure functions are bound
        if not _ensure_gl_funcs():
            return

        # Prefer shader/VAO blit when possible
        try:
            if _init_gl_shader_blit():
                gl.glUseProgram(_gl_program)
                gl.glActiveTexture(0x84C0)  # GL_TEXTURE0
                gl.glBindTexture(0x0DE1, int(handle))
                gl.glBindVertexArray(_gl_vao)
                gl.glDrawArrays(0x0005, 0, 4)  # GL_TRIANGLE_STRIP = 0x0005
                gl.glBindVertexArray(0)
                gl.glBindTexture(0x0DE1, 0)
                gl.glUseProgram(0)
                gl.glFlush()
                return
        except Exception:
            # Fall through to immediate-mode
            pass

        # Constants for immediate-mode fallback
        GL_TEXTURE_2D = 0x0DE1
        GL_PROJECTION = 0x1701
        GL_MODELVIEW = 0x1700
        GL_QUADS = 0x0007

        # Save matrices
        gl.glMatrixMode(GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(0.0, float(w), float(h), 0.0, -1.0, 1.0)

        gl.glMatrixMode(GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        gl.glEnable(GL_TEXTURE_2D)
        gl.glBindTexture(GL_TEXTURE_2D, int(handle))

        gl.glBegin(GL_QUADS)
        # Top-left
        gl.glTexCoord2f(0.0, 0.0)
        gl.glVertex2f(0.0, 0.0)
        # Bottom-left
        gl.glTexCoord2f(0.0, 1.0)
        gl.glVertex2f(0.0, float(h))
        # Bottom-right
        gl.glTexCoord2f(1.0, 1.0)
        gl.glVertex2f(float(w), float(h))
        # Top-right
        gl.glTexCoord2f(1.0, 0.0)
        gl.glVertex2f(float(w), 0.0)
        gl.glEnd()

        gl.glBindTexture(GL_TEXTURE_2D, 0)
        gl.glDisable(GL_TEXTURE_2D)

        gl.glPopMatrix()
        gl.glMatrixMode(GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(GL_MODELVIEW)

        gl.glFlush()
    except Exception:
        # Swallow errors; fall back to flush path in caller
        return


def _init_gl_shader_blit():
    """Initialize a simple shader + VAO/VBO for textured blit using ctypes.

    Returns True on success, False otherwise. This function is conservative
    and will not raise; callers should fall back if it returns False.
    """
    global _gl_program, _gl_vao, _gl_vbo, _gl_blit_ready
    if _gl_blit_ready:
        return True

    gl = _load_gl_lib()
    if gl is None:
        return False

    import ctypes

    try:
        # Bind modern GL functions we need. If any are missing, fail.
        funcs = [
            'glCreateShader', 'glShaderSource', 'glCompileShader', 'glGetShaderiv', 'glGetShaderInfoLog',
            'glCreateProgram', 'glAttachShader', 'glLinkProgram', 'glGetProgramiv', 'glGetProgramInfoLog', 'glDeleteShader',
            'glGenVertexArrays', 'glBindVertexArray', 'glGenBuffers', 'glBindBuffer', 'glBufferData',
            'glEnableVertexAttribArray', 'glVertexAttribPointer', 'glUseProgram', 'glGetUniformLocation', 'glUniform1i',
            'glActiveTexture', 'glDrawArrays'
        ]
        for name in funcs:
            if not hasattr(gl, name):
                return False

        # Setup argtypes/restype for the core functions we will use
        gl.glCreateShader.argtypes = [ctypes.c_uint]
        gl.glCreateShader.restype = ctypes.c_uint
        gl.glShaderSource.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_int)]
        gl.glShaderSource.restype = None
        gl.glCompileShader.argtypes = [ctypes.c_uint]
        gl.glCompileShader.restype = None
        gl.glGetShaderiv.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int)]
        gl.glGetShaderiv.restype = None
        gl.glGetShaderInfoLog.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p]
        gl.glGetShaderInfoLog.restype = None

        gl.glCreateProgram.argtypes = []
        gl.glCreateProgram.restype = ctypes.c_uint
        gl.glAttachShader.argtypes = [ctypes.c_uint, ctypes.c_uint]
        gl.glAttachShader.restype = None
        gl.glLinkProgram.argtypes = [ctypes.c_uint]
        gl.glLinkProgram.restype = None
        gl.glGetProgramiv.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int)]
        gl.glGetProgramiv.restype = None
        gl.glGetProgramInfoLog.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p]
        gl.glGetProgramInfoLog.restype = None
        gl.glDeleteShader.argtypes = [ctypes.c_uint]
        gl.glDeleteShader.restype = None

        gl.glGenVertexArrays.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
        gl.glGenVertexArrays.restype = None
        gl.glBindVertexArray.argtypes = [ctypes.c_uint]
        gl.glBindVertexArray.restype = None
        gl.glGenBuffers.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
        gl.glGenBuffers.restype = None
        gl.glBindBuffer.argtypes = [ctypes.c_uint, ctypes.c_uint]
        gl.glBindBuffer.restype = None
        gl.glBufferData.argtypes = [ctypes.c_uint, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_uint]
        gl.glBufferData.restype = None
        gl.glEnableVertexAttribArray.argtypes = [ctypes.c_uint]
        gl.glEnableVertexAttribArray.restype = None
        gl.glVertexAttribPointer.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.c_void_p]
        gl.glVertexAttribPointer.restype = None
        gl.glUseProgram.argtypes = [ctypes.c_uint]
        gl.glUseProgram.restype = None
        gl.glGetUniformLocation.argtypes = [ctypes.c_uint, ctypes.c_char_p]
        gl.glGetUniformLocation.restype = ctypes.c_int
        gl.glUniform1i.argtypes = [ctypes.c_int, ctypes.c_int]
        gl.glUniform1i.restype = None
        gl.glActiveTexture.argtypes = [ctypes.c_uint]
        gl.glActiveTexture.restype = None
        gl.glDrawArrays.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_int]
        gl.glDrawArrays.restype = None

        # Compile shaders
        VERT_SRC = b"""
        #version 330 core
        layout(location = 0) in vec2 aPos;
        layout(location = 1) in vec2 aTex;
        out vec2 vTex;
        void main() {
            vTex = aTex;
            gl_Position = vec4(aPos, 0.0, 1.0);
        }
        """

        FRAG_SRC = b"""
        #version 330 core
        in vec2 vTex;
        out vec4 FragColor;
        uniform sampler2D uTex;
        void main() {
            FragColor = texture(uTex, vTex);
        }
        """

        GL_VERTEX_SHADER = 0x8B31
        GL_FRAGMENT_SHADER = 0x8B30
        GL_COMPILE_STATUS = 0x8B81
        GL_LINK_STATUS = 0x8B82

        vert = gl.glCreateShader(GL_VERTEX_SHADER)
        src = ctypes.c_char_p(VERT_SRC)
        src_ptr = ctypes.pointer(ctypes.pointer(src))
        length = ctypes.c_int(len(VERT_SRC))
        gl.glShaderSource(vert, 1, src_ptr, ctypes.byref(length))
        gl.glCompileShader(vert)
        status = ctypes.c_int()
        gl.glGetShaderiv(vert, GL_COMPILE_STATUS, ctypes.byref(status))
        if not status.value:
            # compile failed
            buf = ctypes.create_string_buffer(512)
            gl.glGetShaderInfoLog(vert, 512, None, buf)
            return False

        frag = gl.glCreateShader(GL_FRAGMENT_SHADER)
        srcf = ctypes.c_char_p(FRAG_SRC)
        srcf_ptr = ctypes.pointer(ctypes.pointer(srcf))
        lengthf = ctypes.c_int(len(FRAG_SRC))
        gl.glShaderSource(frag, 1, srcf_ptr, ctypes.byref(lengthf))
        gl.glCompileShader(frag)
        gl.glGetShaderiv(frag, GL_COMPILE_STATUS, ctypes.byref(status))
        if not status.value:
            buf = ctypes.create_string_buffer(512)
            gl.glGetShaderInfoLog(frag, 512, None, buf)
            gl.glDeleteShader(vert)
            return False

        prog = gl.glCreateProgram()
        gl.glAttachShader(prog, vert)
        gl.glAttachShader(prog, frag)
        gl.glLinkProgram(prog)
        stat = ctypes.c_int()
        gl.glGetProgramiv(prog, GL_LINK_STATUS, ctypes.byref(stat))
        if not stat.value:
            buf = ctypes.create_string_buffer(512)
            gl.glGetProgramInfoLog(prog, 512, None, buf)
            gl.glDeleteShader(vert)
            gl.glDeleteShader(frag)
            return False

        # shaders can be deleted after linking
        gl.glDeleteShader(vert)
        gl.glDeleteShader(frag)

        # Setup VAO/VBO
        vao = (ctypes.c_uint * 1)()
        vbo = (ctypes.c_uint * 1)()
        gl.glGenVertexArrays(1, vao)
        gl.glGenBuffers(1, vbo)
        gl.glBindVertexArray(vao[0])
        gl.glBindBuffer(0x8892, vbo[0])  # GL_ARRAY_BUFFER = 0x8892

        # Vertex data: (pos.xy, tex.xy) for 4 vertices (triangle strip)
        verts = (ctypes.c_float * 16)(
            -1.0,  1.0, 0.0, 0.0,
            -1.0, -1.0, 0.0, 1.0,
             1.0,  1.0, 1.0, 0.0,
             1.0, -1.0, 1.0, 1.0
        )
        size = ctypes.sizeof(verts)
        GL_STATIC_DRAW = 0x88E4
        gl.glBufferData(0x8892, size, ctypes.cast(verts, ctypes.c_void_p), GL_STATIC_DRAW)

        # attribute 0: position (2 floats), attribute 1: texcoord (2 floats)
        stride = ctypes.c_int(4 * ctypes.sizeof(ctypes.c_float))
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, 0x1406, 0, stride, ctypes.c_void_p(0))  # GL_FLOAT = 0x1406
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 2, 0x1406, 0, stride, ctypes.c_void_p(2 * ctypes.sizeof(ctypes.c_float)))

        gl.glBindBuffer(0x8892, 0)
        gl.glBindVertexArray(0)

        _gl_program = prog
        _gl_vao = vao[0]
        _gl_vbo = vbo[0]
        _gl_blit_ready = True
        return True
    except Exception:
        return False
