import io
import pytest
from PIL import Image, ImageStat

# Skip the whole module if skia isn't installed in the test environment
skia = pytest.importorskip('skia')
from core.io.replay_to_skia_impl import replay_to_skia_canvas


def _surface_to_pil_image(surf):
    img = surf.makeImageSnapshot()
    data = None
    try:
        data = img.encodeToData()
    except Exception:
        data = None
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
            try:
                b = memoryview(data).tobytes()
            except Exception:
                b = None
    assert b is not None
    return Image.open(io.BytesIO(b)).convert('RGBA')


def test_background_op_sets_canvas_color():
    w, h = 64, 48
    surf = skia.Surface(w, h)
    canvas = surf.getCanvas()
    cmds = [{'op': 'background', 'args': {'r': 10, 'g': 20, 'b': 30}}]
    replay_to_skia_canvas(cmds, canvas)
    im = _surface_to_pil_image(surf)
    r, g, b, a = im.getpixel((w // 2, h // 2))
    assert (r, g, b) == (10, 20, 30)


def test_fill_and_rect_draws_colored_rectangle():
    w, h = 64, 48
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    cmds = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        {'op': 'fill', 'args': {'color': (255, 0, 0)}},
        {'op': 'rect', 'args': {'x': w/4, 'y': h/4, 'w': w/2, 'h': h/2}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)
    cx, cy = w // 2, h // 2
    r, g, b, a = im.getpixel((cx, cy))
    assert (r, g, b) == (255, 0, 0)


def test_circle_draws_filled_circle():
    w, h = 64, 48
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    cmds = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        {'op': 'fill', 'args': {'color': (0, 0, 255)}},
        {'op': 'circle', 'args': {'x': w/2, 'y': h/2, 'r': 10}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)
    r, g, b, a = im.getpixel((w // 2, h // 2))
    assert (r, g, b) == (0, 0, 255)


def test_line_draws_stroke():
    w, h = 64, 48
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    cmds = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        {'op': 'line', 'args': {'x1': 5, 'y1': 10, 'x2': 50, 'y2': 10, 'stroke': (255, 255, 255), 'stroke_weight': 2}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)
    # sample along line y=10 between x=10..45; expect at least one non-black pixel
    found = False
    for x in range(10, 45):
        r, g, b, a = im.getpixel((x, 10))
        if (r, g, b) != (0, 0, 0):
            found = True
            break
    assert found, "line did not draw any visible pixels"


def test_image_op_draws_pillow_bytes():
    # create a small pillow image with a green square
    w, h = 32, 32
    pil = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    draw = Image.new('RGBA', (w, h))
    base = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    from PIL import ImageDraw
    idraw = ImageDraw.Draw(base)
    idraw.rectangle([8, 8, 23, 23], fill=(0, 255, 0, 255))
    raw = base.tobytes()

    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    cmds = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        {'op': 'image', 'args': {'image_bytes': raw, 'image_size': (w, h), 'image_mode': 'RGBA', 'x': 0, 'y': 0}},
    ]
    replay_to_skia_canvas(cmds, c)
    im = _surface_to_pil_image(surf)
    # pixel inside green square
    r, g, b, a = im.getpixel((12, 12))
    assert (r, g, b) == (0, 255, 0)


def test_additive_blend_increases_brightness():
    w, h = 64, 48
    area = (w//4, h//4, w*3//4, h*3//4)

    def mean_red_for_sequence(cmds):
        surf = skia.Surface(w, h)
        c = surf.getCanvas()
        replay_to_skia_canvas(cmds, c)
        im = _surface_to_pil_image(surf)
        st = ImageStat.Stat(im)
        return st.mean[0]

    # two semi-transparent red draws with default blend (src_over)
    cmds_default = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        {'op': 'fill', 'args': {'color': (255, 0, 0)}},
        {'op': 'rect', 'args': {'x': area[0], 'y': area[1], 'w': area[2]-area[0], 'h': area[3]-area[1], 'fill_alpha': 0.5}},
        {'op': 'rect', 'args': {'x': area[0], 'y': area[1], 'w': area[2]-area[0], 'h': area[3]-area[1], 'fill_alpha': 0.5}},
    ]

    # same but with blend_mode ADD
    cmds_add = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        {'op': 'blend_mode', 'args': {'mode': 'ADD'}},
        {'op': 'fill', 'args': {'color': (255, 0, 0)}},
        {'op': 'rect', 'args': {'x': area[0], 'y': area[1], 'w': area[2]-area[0], 'h': area[3]-area[1], 'fill_alpha': 0.5}},
        {'op': 'rect', 'args': {'x': area[0], 'y': area[1], 'w': area[2]-area[0], 'h': area[3]-area[1], 'fill_alpha': 0.5}},
    ]

    mean_default = mean_red_for_sequence(cmds_default)
    mean_add = mean_red_for_sequence(cmds_add)
    assert mean_add >= mean_default, f"expected ADD blend to be >= default ({mean_add} vs {mean_default})"
