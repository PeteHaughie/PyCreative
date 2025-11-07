import sys
import os

# Ensure local package imports work when pytest is invoked from the repo root
sys.path.insert(0, os.path.abspath('src'))

import pycreative
import pycreative.graphics as gfx


def _make_engine_with_sketch_dir(sketch_dir: str):
    """Create a minimal fake engine whose sketch module lives in sketch_dir.

    The object exposes `_sketch_module.__file__` which the path resolution
    helper in `load_shader` relies on.
    """
    class _SketchModule:
        pass

    sm = _SketchModule()
    setattr(sm, '__file__', os.path.join(sketch_dir, 'sketch.py'))

    class _Engine:
        pass

    eng = _Engine()
    eng._sketch_module = sm
    # minimal graphics buffer to satisfy shader() recording if used
    try:
        from core.graphics import GraphicsBuffer

        eng.graphics = GraphicsBuffer()
    except Exception:
        eng.graphics = None
    return eng


def test_load_shader_and_uniforms(tmp_path):
    # Arrange: create a sketch directory with a data/ subfolder and a frag file
    sketch_dir = tmp_path / 'sketch_dir'
    data_dir = sketch_dir / 'data'
    data_dir.mkdir(parents=True)
    frag_file = data_dir / 'blur.glsl'
    frag_text = '// fragment shader\nvoid main() { /* frag */ }\n'
    frag_file.write_text(frag_text, encoding='utf-8')

    # Create a minimal sketch.py so resolution logic can find the dir
    (sketch_dir / 'sketch.py').write_text('# sketch placeholder', encoding='utf-8')

    eng = _make_engine_with_sketch_dir(str(sketch_dir))
    pycreative.set_current_engine(eng)

    # Act: load the shader using the fragment filename only
    s = gfx.load_shader('blur.glsl')

    # Assert: a PCShader was returned and contains the fragment source
    assert s is not None
    assert isinstance(s, gfx.PCShader)
    assert 'fragment shader' in s.frag_source

    # Test the uniform setter
    s.set('time', 1.234)
    assert s.get_uniform('time') == (1.234,)


def test_load_shader_missing_returns_none(tmp_path, capsys):
    sketch_dir = tmp_path / 'sketch_dir2'
    sketch_dir.mkdir()
    (sketch_dir / 'sketch.py').write_text('# sketch placeholder', encoding='utf-8')
    eng = _make_engine_with_sketch_dir(str(sketch_dir))
    pycreative.set_current_engine(eng)

    # Try to load a non-existent file
    res = gfx.load_shader('not_here.glsl')
    assert res is None
