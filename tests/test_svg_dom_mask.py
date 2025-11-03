import os
import pytest
import io

try:
    import skia
except Exception:  # pragma: no cover - skip if skia unavailable
    skia = None

from pycreative.shape.skia_svg_adapter import load_shape
from core.io import replay_to_skia_impl


@pytest.mark.skipif(skia is None, reason="skia not available")
def test_svg_dom_mask_preserves_alpha_and_shape():
    """Render a small SVG DOM with use_style=False and a semi-transparent fill.

    We expect the DOM-rendered mask to produce non-empty per-pixel alpha values
    and the composed colored image to contain partial alpha (not just a fully
    opaque bounding box). This guards the DstIn recolor + alpha preservation
    behaviour implemented in the replayer.
    """
    # Locate an example SVG that ships with the repo
    svg_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "examples",
        "Generative Gestaltung",
        "01_P",
        "P_2_1_1_04",
        "data",
        "module_1.svg",
    )
    svg_path = os.path.normpath(svg_path)
    assert os.path.exists(svg_path), f"SVG not found: {svg_path}"

    pcshape = load_shape(svg_path)
    dom = getattr(pcshape, "_svg_dom", None)
    assert dom is not None, "skia SVGDOM not available on this PCShape"

    # Use intrinsic size for a simple 1:1 render
    iw = int(max(1, round(float(pcshape.width or 100))))
    ih = int(max(1, round(float(pcshape.height or 100))))

    # Make a skia surface and canvas (transparent initially)
    info = skia.ImageInfo.Make(iw, ih, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
    surf = skia.Surface.MakeRaster(info)
    assert surf is not None
    canvas = surf.getCanvas()
    # ensure canvas starts transparent
    try:
        canvas.clear(0)
    except Exception:
        try:
            canvas.clear(skia.Color4f(0, 0, 0, 0))
        except Exception:
            pass

    # Build a single svg_dom command: disable styles and provide a semi-transparent fill
    cmd = {
        "op": "svg_dom",
        "args": {
            "dom": dom,
            "width": iw,
            "height": ih,
            "intrinsic_width": iw,
            "intrinsic_height": ih,
            "use_style": False,
            "fill": (0, 130, 164),
            "fill_alpha": 0.5,
            "shape_mode": "CORNER",
        },
    }

    # Replay into our canvas
    replay_to_skia_impl.replay_to_skia_canvas([cmd], canvas)

    # Snapshot and inspect pixels
    img = surf.makeImageSnapshot()
    data = img.encodeToData()
    assert data is not None

    # Extract bytes and examine alpha distribution with PIL (if available)
    b = None
    if hasattr(data, "toBytes"):
        b = data.toBytes()
    elif hasattr(data, "tobytes"):
        b = data.tobytes()
    else:
        b = bytes(data)

    from PIL import Image
    im = Image.open(io.BytesIO(b)).convert("RGBA")
    w, h = im.size

    # Check we have some non-background pixels. Use getpixel() which has
    # a predictable return type for mypy (tuple[int, int, int, int]).
    bg = (255, 255, 255, 255)
    nonbg = 0
    partial_alpha = 0
    import typing

    for y in range(h):
        for x in range(w):
            rgba = typing.cast(tuple[int, int, int, int], im.getpixel((x, y)))
            # rgba is a 4-tuple (r,g,b,a)
            if rgba[:3] != (255, 255, 255) or rgba[3] != 0:
                nonbg += 1
            if 0 < rgba[3] < 255:
                partial_alpha += 1

    assert nonbg > 0, "No non-background pixels rendered by svg_dom"
    assert partial_alpha > 0, "Expected some pixels with partial alpha (<255) to exist"
