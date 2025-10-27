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


def test_point_fill_renders_pixel():
    w, h = 40, 30
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    cx, cy = w/2, h/2
    cmds = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        # Per API, fill should NOT affect `point` primitives. Ensure that a
        # filled-point does not change the pixel at the center.
        {'op': 'point', 'args': {'x': cx, 'y': cy, 'fill': (123, 45, 67)}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)
    r, g, b, a = im.getpixel((int(cx), int(cy)))
    # Expect unchanged background (black)
    assert (r, g, b) == (0, 0, 0)


def test_point_stroke_renders_pixel():
    w, h = 40, 30
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    cx, cy = w/2, h/2
    cmds = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        # Stroked point should render visible pixels
        {'op': 'point', 'args': {'x': cx, 'y': cy, 'stroke': (10, 200, 10), 'stroke_weight': 3}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)
    # center might be background if stroke is hollow; sample nearby pixels
    # Allow for anti-aliased/blended stroke — check for a nearby pixel with
    # a dominant green channel instead of requiring exact equality.
    found = False
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            px = im.getpixel((int(cx + dx), int(cy + dy)))[:3]
            r, g, b = px
            if g >= 120 and r <= 80 and b <= 80:
                found = True
                break
        if found:
            break
    assert found, f'stroke point did not produce visible stroke pixels (samples around center: {px})'


def test_point_with_zero_stroke_weight_is_not_drawn():
    w, h = 40, 30
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    cx, cy = w/2, h/2
    cmds = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        # stroke_weight 0 should not render
        {'op': 'point', 'args': {'x': cx, 'y': cy, 'stroke': (10, 200, 10), 'stroke_weight': 0}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)
    r, g, b = im.getpixel((int(cx), int(cy)))[:3]
    assert (r, g, b) == (0, 0, 0)


def test_fill_alpha_is_honored():
    # draw a filled circle with 50% alpha over a white background and expect
    # the resulting pixel to be a mid-gray rather than full black.
    w, h = 40, 40
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    cx, cy = w/2, h/2
    cmds = [
        {'op': 'background', 'args': {'r': 255, 'g': 255, 'b': 255}},
        {'op': 'circle', 'args': {'x': cx, 'y': cy, 'r': 8, 'fill': (0, 0, 0), 'fill_alpha': 0.5}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)
    r, g, b = im.getpixel((int(cx), int(cy)))[:3]
    # Expect a gray-ish pixel (between white and black)
    assert 20 < r < 240 and 20 < g < 240 and 20 < b < 240 and not (r == 0 and g == 0 and b == 0)


def test_stroke_alpha_is_honored():
    # draw a stroked circle (no fill) in green over a white background with
    # 50% stroke alpha; expect the sampled pixel to be a blend (not pure
    # white and not pure green)
    w, h = 60, 60
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    cx, cy = w/2, h/2
    cmds = [
        {'op': 'background', 'args': {'r': 255, 'g': 255, 'b': 255}},
        # stroked circle with visible stroke weight and alpha 0.5
        {'op': 'circle', 'args': {'x': cx, 'y': cy, 'r': 10, 'stroke': (0, 200, 0), 'stroke_weight': 6, 'stroke_alpha': 0.5}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)
    # Sample a pixel on the expected stroke ring (approx at cx + r, cy)
    sample_x = int(cx + 10)
    sample_y = int(cy)
    r, g, b = im.getpixel((sample_x, sample_y))[:3]
    # After 50% alpha over white, expect green channel reduced from 200 toward 255
    assert not (r == 255 and g == 255 and b == 255), 'stroke pixel should not be pure white'
    assert g > r and g > b, f'stroke sample not green-dominant: {(r,g,b)}'
