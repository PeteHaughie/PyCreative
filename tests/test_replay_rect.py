import os
from PIL import Image
import skia
from core.io.replay_to_skia_impl import replay_to_skia_canvas


def test_replay_draws_rect():
    # small surface
    w, h = 64, 48
    surf = skia.Surface(w, h)
    c = surf.getCanvas()

    # commands: clear black, set fill to red, draw centered rect
    cmds = [
        {'op': 'background', 'args': {'r': 0, 'g': 0, 'b': 0}},
        {'op': 'fill', 'args': {'color': (255, 0, 0)}},
        {'op': 'rect', 'args': {'x': w/4, 'y': h/4, 'w': w/2, 'h': h/2}},
    ]

    # replay onto canvas
    replay_to_skia_canvas(cmds, c)

    # snapshot to image bytes and inspect pixels
    img = surf.makeImageSnapshot()
    data = img.encodeToData()
    assert data is not None
    # extract bytes
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

    # write to a temp file and open with Pillow for easy pixel checks
    tmp = os.path.join(os.getcwd(), 'tests', 'tmp_replay_rect.png')
    with open(tmp, 'wb') as f:
        f.write(b)

    im = Image.open(tmp).convert('RGBA')
    # check center pixel is red
    cx, cy = int(w/2), int(h/2)
    r, g, b_, a = im.getpixel((cx, cy))
    assert (r, g, b_) == (255, 0, 0)

    # cleanup
    try:
        os.remove(tmp)
    except Exception:
        pass
