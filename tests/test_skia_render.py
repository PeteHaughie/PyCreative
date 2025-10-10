import textwrap
from pathlib import Path
import pytest

from pycreative.shape import load_svg


def write_svg(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "test.svg"
    p.write_text(textwrap.dedent(content))
    return p


@pytest.mark.skipif(not __import__('importlib').util.find_spec('skia'), reason='skia not available')
def test_skia_render_shorthand(tmp_path: Path):
    svg = """
    <svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'>
      <path d='M 50 50 c 10 10 30 10 40 0 s 30 -20 40 0' fill='#ff0000' stroke='#000000' stroke-width='2'/>
    </svg>
    """
    p = write_svg(tmp_path, svg)
    shp = load_svg(str(p))
    assert shp is not None
    # rasterize via skia_renderer
    from pycreative.shape.skia_renderer import skia_rasterize_pshape
    im = skia_rasterize_pshape(shp, 200, 200)
    assert im is not None
    outdir = Path('tests/assets/out_snapshots/skia')
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / 'test_skia_render_shorthand.png'
    im.save(out)


@pytest.mark.skipif(not __import__('importlib').util.find_spec('skia'), reason='skia not available')
def test_skia_render_s_shorthand(tmp_path: Path):
    svg = """
    <svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'>
      <path d='M 10 10 C 20 20 40 20 50 10 S 80  -10 90 10' fill='none' stroke='#00ff00' stroke-width='2'/>
    </svg>
    """
    p = write_svg(tmp_path, svg)
    shp = load_svg(str(p))
    assert shp is not None
    from pycreative.shape.skia_renderer import skia_rasterize_pshape
    im = skia_rasterize_pshape(shp, 200, 200)
    assert im is not None
    outdir = Path('tests/assets/out_snapshots/skia')
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / 'test_skia_render_s_shorthand.png'
    im.save(out)


@pytest.mark.skipif(not __import__('importlib').util.find_spec('skia'), reason='skia not available')
def test_skia_render_t_shorthand(tmp_path: Path):
    svg = """
    <svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'>
      <path d='M 20 20 Q 40 0 60 20 T 100 20' fill='none' stroke='#0000ff' stroke-width='2'/>
    </svg>
    """
    p = write_svg(tmp_path, svg)
    shp = load_svg(str(p))
    assert shp is not None
    from pycreative.shape.skia_renderer import skia_rasterize_pshape
    im = skia_rasterize_pshape(shp, 200, 200)
    assert im is not None
    outdir = Path('out_snapshots/skia')
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / 'test_skia_render_t_shorthand.png'
    im.save(out)
