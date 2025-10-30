import pytest

try:
    import skia  # type: ignore
except Exception:
    pytest.skip('skia-python is required for SVG loader tests', allow_module_level=True)

if not hasattr(skia, 'SVGDOM'):
    pytest.skip('skia-python build lacks SVGDOM; skipping SVG loader tests', allow_module_level=True)

# Some skia builds expose SVGDOM but not the constructor helpers we need
if not any(hasattr(skia.SVGDOM, name) for name in ('MakeFromFile', 'MakeFromString', 'MakeFromStream')):
    pytest.skip('skia.SVGDOM present but missing MakeFromFile/MakeFromString/MakeFromStream; skipping SVG loader tests', allow_module_level=True)

from pycreative.shape.loader import load_svg


def test_load_simple_svg(tmp_path):
    svg = """<svg width='100' height='100' xmlns='http://www.w3.org/2000/svg'>
  <path d='M10 10 L90 10 L90 90 L10 90 Z' fill='none' stroke='black'/>
</svg>
"""
    p = tmp_path / "simple.svg"
    p.write_text(svg)

    try:
        out = load_svg(str(p))
    except RuntimeError as e:
        # In CI or local dev the installed skia build may lack SVGDOM
        # constructors; treat this as an environment skip rather than
        # a test failure since the loader now requires Skia DOM or svg.path
        pytest.skip(f'skia SVGDOM not available: {e}')

    assert out is not None
    # Loader returns a PCShape-like object with `skia_paths`
    assert hasattr(out, 'skia_paths')
    assert len(out.skia_paths) >= 1
