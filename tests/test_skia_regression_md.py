from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance
import skia


def _rasterize_native_skia(svg_path: Path, w: int = 400, h: int = 400):
    try:
        mem = skia.MemoryStream(svg_path.read_bytes())
        dom = skia.SVGDOM.MakeFromStream(mem)
        if hasattr(dom, 'setContainerSize'):
            dom.setContainerSize(skia.Size(w, h))
        info = skia.ImageInfo.Make(w, h, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType)
        surf = skia.Surface.MakeRaster(info)
        canvas = surf.getCanvas()
        canvas.clear(skia.ColorWHITE)
        dom.render(canvas)
        img = surf.makeImageSnapshot()
        data = img.encodeToData()
        try:
            b = data.toBytes()
        except Exception:
            try:
                b = bytes(data)
            except Exception:
                return None
        im = Image.open(__import__('io').BytesIO(b)).convert('RGBA')
        return im
    except Exception:
        return None


def _compute_diff(img1: Image.Image, img2: Image.Image) -> Image.Image:
    # Ensure same size
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)
    # absolute difference per-channel
    diff = ImageChops.difference(img1, img2)
    # amplify differences for visibility
    enhancer = ImageEnhance.Brightness(diff)
    diff = enhancer.enhance(4.0)
    return diff


def test_write_regression_md():
    assets = Path('tests/assets')
    outdir = assets / 'out_snapshots' / 'skia'
    outdir.mkdir(parents=True, exist_ok=True)
    md = Path('tests/current-regression.md')
    lines = ['```markdown\n', '# Skia current regression images\n\n']

    svgs = sorted(assets.glob('*.svg'))
    if not svgs:
        lines.append('_no svg assets found_\n')
        lines.append('```\n')
        md.write_text(''.join(lines))
        return

    from pycreative.shape import load_svg
    from pycreative.shape.skia_renderer import skia_rasterize_pshape_cached

    for svg in svgs:
        stem = svg.stem
        api_img_path = outdir / f"{stem}_skia.png"
        native_img_path = outdir / f"{stem}_native.png"
        diff_img_path = outdir / f"{stem}_diff.png"

        # Ensure API-rendered image exists (produce if missing)
        shp = load_svg(str(svg))
        if shp is None:
            lines.append(f'## {stem} - failed to load via API\n')
            lines.append('\n')
            continue
        api_im = skia_rasterize_pshape_cached(shp, 400, 400)
        if api_im is not None:
            api_im.save(api_img_path)

        # Produce native Skia render
        native_im = _rasterize_native_skia(svg, 400, 400)
        if native_im is not None:
            native_im.save(native_img_path)

        # Compute diff if both images exist
        if api_img_path.exists() and native_img_path.exists():
            a = Image.open(api_img_path).convert('RGBA')
            b = Image.open(native_img_path).convert('RGBA')
            diff = _compute_diff(a, b)
            diff.save(diff_img_path)

        # Write markdown entry: show API, Native, Diff images
        lines.append(f'## {stem}\n')
        if api_img_path.exists():
            lines.append(f"API-rendered: <img src=\"../{api_img_path.as_posix()}\">\n")
        else:
            lines.append('API-rendered: _missing_\n')
        if native_img_path.exists():
            lines.append(f"Native Skia: <img src=\"../{native_img_path.as_posix()}\">\n")
        else:
            lines.append('Native Skia: _missing_\n')
        if diff_img_path.exists():
            lines.append(f"Diff: <img src=\"../{diff_img_path.as_posix()}\">\n\n")
        else:
            lines.append('Diff: _missing_\n\n')

    lines.append('```\n')
    md.write_text(''.join(lines))

