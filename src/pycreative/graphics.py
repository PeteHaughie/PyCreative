"""Thin public graphics shims re-exporting core graphics helpers.

These functions delegate to the current engine (set via
`pycreative.set_current_engine`) so tests and examples can use the
`pycreative.graphics` namespace without importing core internals.
"""
from __future__ import annotations


from . import _get_engine

try:
    from core.graphics import PCGraphics as PCGraphics
except Exception:
    PCGraphics = None


# Registry of loaded PCShader objects so presenters can compile them.
try:
    import weakref

    _REGISTERED_SHADERS = weakref.WeakSet()
except Exception:
    _REGISTERED_SHADERS = set()


# Minimal default passthrough vertex shader used when only a fragment
# shader is supplied. This keeps fragment-only sketches working without
# requiring authors to always provide a vertex shader.
DEFAULT_VERTEX_SHADER = """
attribute vec2 position;
attribute vec2 texcoord0;
varying vec2 v_texcoord;
void main() {
    v_texcoord = texcoord0;
    gl_Position = vec4(position, 0.0, 1.0);
}
"""


def blend_mode(mode: str) -> None:
    eng = _get_engine()
    try:
        # Try to delegate to the SimpleSketchAPI for consistent behaviour
        from core.engine.api.simple import SimpleSketchAPI

        return SimpleSketchAPI(eng).blend_mode(mode)
    except Exception:
        # Fallback: persist on engine object so replayers and presenters
        # can inspect the chosen blend mode.
        try:
            setattr(eng, 'blend_mode', str(mode))
        except Exception:
            pass
    return None


class PCShader:
    """Minimal PCShader shim used by examples and tests.

    This is a lightweight representation that stores shader source and
    supports simple uniform set/get used by tests. Real rendering backends
    provide a richer implementation; this shim keeps the public API stable
    for examples and headless tests.
    """

    def __init__(self, frag_source: str | None = None, vert_source: str | None = None):
        self.frag_source = frag_source
        # Provide a default passthrough vertex shader when none is given so
        # presenters can compile fragment-only shaders.
        self.vert_source = vert_source if vert_source is not None else DEFAULT_VERTEX_SHADER
        self._uniforms: dict[str, tuple] = {}
        # compiled GL program id (when compiled by a presenter)
        self._program: int | None = None
        # cache of uniform locations after program link
        self._uniform_locs: dict[str, int] = {}
        # register for runtime presenters to compile
        try:
            _REGISTERED_SHADERS.add(self)
        except Exception:
            try:
                # best-effort fallback
                if isinstance(_REGISTERED_SHADERS, set):
                    _REGISTERED_SHADERS.add(self)
            except Exception:
                pass

    def set(self, name: str, *values):
        try:
            # store as tuple for deterministic comparisons in tests
            self._uniforms[str(name)] = tuple(values)
        except Exception:
            pass

        # If compiled into a GL program, attempt to set the uniform immediately
        try:
            if getattr(self, '_program', None) is not None:
                from pyglet import gl
                loc = self._uniform_locs.get(str(name))
                if loc is None:
                    loc = gl.glGetUniformLocation(self._program, str(name).encode('utf-8'))
                    try:
                        self._uniform_locs[str(name)] = int(loc)
                    except Exception:
                        pass
                # Best-effort support for common uniform types:
                # - single float -> glUniform1f
                # - vec2/vec3/vec4 floats -> glUniform2f/3f/4f
                # - integer/sampler -> glUniform1i (and try to bind pyglet textures)
                try:
                    # Try float path first
                    vals_f = tuple(float(v) for v in values)
                    gl.glUseProgram(self._program)
                    if len(vals_f) == 1:
                        gl.glUniform1f(int(loc), float(vals_f[0]))
                    elif len(vals_f) == 2:
                        gl.glUniform2f(int(loc), vals_f[0], vals_f[1])
                    elif len(vals_f) == 3:
                        gl.glUniform3f(int(loc), vals_f[0], vals_f[1], vals_f[2])
                    elif len(vals_f) == 4:
                        gl.glUniform4f(int(loc), vals_f[0], vals_f[1], vals_f[2], vals_f[3])
                    gl.glUseProgram(0)
                except Exception:
                    # Fallback: try integer/sampler path. This handles texture samplers
                    # (pyglet texture objects often expose an `id` attribute) and integer
                    # uniform values.
                    try:
                        gl.glUseProgram(self._program)
                        # If a single value and it has an `id` attribute, bind it as a
                        # GL_TEXTURE_2D to texture unit 0 and set the sampler uniform to 0.
                        if len(values) == 1:
                            v = values[0]
                            tex_id = None
                            try:
                                tex_id = getattr(v, 'id', None)
                            except Exception:
                                tex_id = None
                            if tex_id is not None:
                                # bind texture unit 0
                                try:
                                    gl.glActiveTexture(gl.GL_TEXTURE0)
                                    gl.glBindTexture(gl.GL_TEXTURE_2D, int(tex_id))
                                    gl.glUniform1i(int(loc), 0)
                                except Exception:
                                    pass
                            else:
                                # try integer uniform
                                try:
                                    ival = int(values[0])
                                    gl.glUniform1i(int(loc), ival)
                                except Exception:
                                    pass
                        else:
                            # multiple integer components: try 2i/3i/4i
                            try:
                                ivals = tuple(int(v) for v in values)
                                if len(ivals) == 2:
                                    gl.glUniform2i(int(loc), ivals[0], ivals[1])
                                elif len(ivals) == 3:
                                    gl.glUniform3i(int(loc), ivals[0], ivals[1], ivals[2])
                                elif len(ivals) == 4:
                                    gl.glUniform4i(int(loc), ivals[0], ivals[1], ivals[2], ivals[3])
                            except Exception:
                                pass
                        gl.glUseProgram(0)
                    except Exception:
                        pass
        except Exception:
            pass

    def get_uniform(self, name: str):
        return self._uniforms.get(str(name))


def _resolve_sketch_path(filename: str) -> str | None:
    """Resolve a filename relative to the current sketch module.

    Looks for `data/` subfolder first, then the sketch directory. Returns
    an absolute path or None if the file can't be found.
    """
    try:
        eng = _get_engine()
    except Exception:
        eng = None
    if eng is None:
        return None
    try:
        smod = getattr(eng, '_sketch_module', None)
        if smod is None:
            return None
        sf = getattr(smod, '__file__', None)
        if not sf:
            return None
        import os
        sketch_dir = os.path.dirname(os.path.abspath(sf))
        data_path = os.path.join(sketch_dir, 'data', filename)
        if os.path.exists(data_path):
            return data_path
        sketch_path = os.path.join(sketch_dir, filename)
        if os.path.exists(sketch_path):
            return sketch_path
    except Exception:
        pass
    return None


def load_shader(frag_filename: str, vert_filename: str | None = None):
    """Load a fragment (and optional vertex) shader and return a PCShader.

    Returns None when the file is missing or cannot be read.
    """
    try:
        frag_path = _resolve_sketch_path(frag_filename)
        if frag_path is None:
            return None
        with open(frag_path, 'r', encoding='utf-8') as fh:
            frag_src = fh.read()
    except Exception:
        return None
    vert_src = None
    if vert_filename is not None:
        try:
            vpath = _resolve_sketch_path(vert_filename)
            if vpath is not None:
                with open(vpath, 'r', encoding='utf-8') as vh:
                    vert_src = vh.read()
        except Exception:
            vert_src = None

    return PCShader(frag_source=frag_src, vert_source=vert_src)


def create_graphics(w: int, h: int):
    """Public shim to create an offscreen `PCGraphics` surface.

    Delegates to an engine-registered implementation when available,
    otherwise uses the core `create_graphics` fallback.
    """
    try:
        eng = _get_engine()
    except Exception:
        eng = None

    # Prefer an engine-registered implementation
    try:
        if eng is not None:
            fn = eng.api.get('create_graphics')
            if callable(fn):
                try:
                    return fn(w, h)
                except Exception:
                    pass
    except Exception:
        pass

    try:
        # fallback to core implementation
        from core.graphics import create_graphics as _cg

        return _cg(int(w), int(h))
    except Exception:
        return None


__all__ = ['blend_mode', 'PCShader', 'load_shader', 'create_graphics', 'PCGraphics']
