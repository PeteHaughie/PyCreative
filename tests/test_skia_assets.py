from pathlib import Path
import pytest

from pycreative.shape import load_svg


@pytest.mark.skipif(not __import__('importlib').util.find_spec('skia'), reason='skia not available')
def test_rasterize_assets_svgs():
    assets = Path('tests/assets')
    outdir = assets / 'out_snapshots' / 'skia'
    outdir.mkdir(parents=True, exist_ok=True)
    svgs = sorted(assets.glob('*.svg'))
    assert svgs, 'no svg assets found in tests/assets'
    from pycreative.shape.skia_renderer import skia_rasterize_pshape_cached
    for svg in svgs:
        shp = load_svg(str(svg))
        assert shp is not None, f'failed to load {svg}'
        im = skia_rasterize_pshape_cached(shp, 400, 400)
        assert im is not None, f'skia raster failed for {svg}'
        out = outdir / f"{svg.stem}_skia.png"
        im.save(out)
        assert out.exists()
