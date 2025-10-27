import io
import pytest
from PIL import Image

skia = pytest.importorskip('skia')
from core.io.replay_to_skia_impl import replay_to_skia_canvas


def _surface_to_pil_image(surf):
    img = surf.makeImageSnapshot()
    data = img.encodeToData()
    assert data is not None
    b = None
    for fn in ("toBytes", "asBytes", "tobytes"):
        if hasattr(data, fn):
            try:
                b = getattr(data, fn)()
                break
            except Exception:
                b = None
    if b is None:
        try:
            b = bytes(data)
        except Exception:
            b = None
    assert b is not None
    return Image.open(io.BytesIO(b)).convert('RGBA')


def test_stroke_only_rect():
    w, h = 80, 60
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    cmds = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        # no fill, only stroke
        {'op': 'rect', 'args': {'x': 10, 'y': 10, 'w': 60, 'h': 40, 'stroke': (255, 255, 255), 'stroke_weight': 3}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)

    # center inside rect should remain black (no fill)
    cx, cy = 40, 30
    assert im.getpixel((cx, cy))[:3] == (0, 0, 0)

    # sample a wide perimeter region - expect some non-background pixels
    found = False
    left, top, right, bottom = 10, 10, 10 + 60, 10 + 40
    for y in range(top - 3, top + 6):
        for x in range(left + 1, right - 1):
            if im.getpixel((x, y))[:3] != (0, 0, 0):
                found = True
                break
        if found:
            break
    # also check vertical edges if not found yet
    if not found:
        for x in range(left - 3, left + 6):
            for y in range(top + 1, bottom - 1):
                if im.getpixel((x, y))[:3] != (0, 0, 0):
                    found = True
                    break
            if found:
                break
    assert found, "stroke-only rect did not draw border pixels (checked perimeter region)"


def test_stroke_only_circle():
    w, h = 80, 60
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    cmds = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        {'op': 'circle', 'args': {'x': w/2, 'y': h/2, 'r': 15, 'stroke': (0, 255, 0), 'stroke_weight': 4}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)

    # center should be background
    assert im.getpixel((w//2, h//2))[:3] == (0, 0, 0)

    # sample a perimeter point (rightmost) and expect green
    rx = int(w//2 + 15)
    ry = int(h//2)
    r, g, b = im.getpixel((rx, ry))[:3]
    assert (r, g, b) != (0, 0, 0), "stroke-only circle did not render stroke pixels"


def test_stroke_weight_thickness():
    w, h = 80, 60
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    # draw two concentric circles with different stroke weights
    cmds = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        {'op': 'circle', 'args': {'x': w/2, 'y': h/2, 'r': 12, 'stroke': (255, 0, 0), 'stroke_weight': 1}},
        {'op': 'circle', 'args': {'x': w/2, 'y': h/2, 'r': 12, 'stroke': (255, 0, 0), 'stroke_weight': 6}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)

    # check a pixel slightly inside the outer stroke area which should be set by thicker stroke
    sample = im.getpixel((int(w/2 + 12 - 2), int(h/2)))[:3]
    assert sample != (0, 0, 0), "thicker stroke did not produce visible pixels at expected offset"
