import os
from PIL import Image, ImageStat
import skia

from core.io.replay_to_skia_impl import replay_to_skia_canvas


def test_pcg_primitives_render_and_visual_output():
    """Draw rect/ellipse/square/circle into a PCGraphics offscreen, replay to Skia,
    write a visual PNG and assert each primitive's color is present.
    """
    # Create headless engine and SimpleSketchAPI
    from core.engine.impl import Engine
    from core.graphics import PCGraphics

    eng = Engine(sketch_module=None, headless=True)
    # create an offscreen PCGraphics bound to this engine so end_draw() records
    w, h = 300, 200
    pg = PCGraphics(w, h, engine=eng)

    # draw the four primitives with distinct fills
    pg.begin_draw()
    pg.background(0)
    pg.fill(255, 0, 0)
    pg.rect(20, 20, 100, 60)
    pg.fill(0, 255, 0)
    pg.ellipse(180, 60, 80, 40)
    pg.fill(0, 0, 255)
    pg.square(10, 150, 50)
    pg.fill(255)
    pg.circle(250, 150, 80)
    pg.end_draw()

    # retrieve the recorded offscreen op from engine.graphics
    rec = getattr(eng, 'graphics', None)
    assert rec is not None
    off_ops = [c for c in rec.commands if c.get('op') == 'offscreen']
    assert len(off_ops) >= 1
    off = off_ops[-1]
    args = off.get('args', {})
    inner_ops = args.get('ops', [])
    assert inner_ops, 'no inner ops recorded in offscreen'

    # replay inner ops onto a Skia surface
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    replay_to_skia_canvas(inner_ops, c)

    # snapshot to bytes and write PNG for visual inspection
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

    tmp = os.path.join(os.getcwd(), 'tests', 'tmp_pcg_primitives.png')
    with open(tmp, 'wb') as f:
        f.write(b)

    im = Image.open(tmp).convert('RGBA')
    px = im.load()

    # helper: scan for presence and bounding box of a color
    def find_color_bounds(rmin, gmin, bmin, rmax=255, gmax=255, bmax=255, threshold=10):
        w_, h_ = im.size
        count = 0
        bx = [w_, h_, 0, 0]
        for y in range(h_):
            for x in range(w_):
                r, g, b_, a = px[x, y]
                if a == 0:
                    continue
                if rmin - threshold <= r <= rmax and gmin - threshold <= g <= gmax and bmin - threshold <= b_ <= bmax:
                    count += 1
                    if x < bx[0]: bx[0] = x
                    if y < bx[1]: bx[1] = y
                    if x > bx[2]: bx[2] = x
                    if y > bx[3]: bx[3] = y
        return count, tuple(bx)

    # expect red rect, green ellipse, blue square, white circle
    red_count, red_bbox = find_color_bounds(200, 0, 0)
    green_count, green_bbox = find_color_bounds(0, 200, 0)
    blue_count, blue_bbox = find_color_bounds(0, 0, 200)
    white_count, white_bbox = find_color_bounds(240, 240, 240)

    assert red_count > 100, f'red rect not present or too small ({red_count})'
    assert green_count > 50, f'green ellipse not present ({green_count})'
    assert blue_count > 50, f'blue square not present ({blue_count})'
    assert white_count > 100, f'white circle not present ({white_count})'

    # leave the PNG in tests/ for visual inspection; tests may cleanup elsewhere
