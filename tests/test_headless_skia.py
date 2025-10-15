import hashlib
import skia


def render_frame(w, h, frame_idx):
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    bg = 0.05 + (frame_idx % 60) / 60.0 * 0.6
    try:
        c.clear(skia.Color4f(bg, bg * 0.9, bg * 0.8, 1.0))
    except Exception:
        c.clear(0xFF19191F)
    # draw simple primitives
    cx, cy = w // 2, h // 2
    r = 32
    p = skia.Paint()
    p.setAntiAlias(True)
    try:
        p.setColor(skia.Color4f(0.2, 0.6 + frame_idx * 0.01, 0.9, 1.0))
    except Exception:
        p.setColor(0xFF3399FF)
    c.drawCircle(cx + frame_idx * 2, cy, r, p)
    # snapshot
    img = surf.makeImageSnapshot()
    data = img.encodeToData()
    assert data is not None
    # skia.Data may expose different APIs across skia-python versions; try several
    b = None
    for fn in ("toBytes", "asBytes"):
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
    assert b is not None, "could not extract bytes from skia.Data"
    return b


def test_headless_frames_differ():
    b0 = render_frame(200, 150, 0)
    b1 = render_frame(200, 150, 1)
    assert b0 != b1, "Two consecutive frames should not be identical"
    # quick sanity: both are valid PNGs by header
    assert b0[:8] == b"\x89PNG\r\n\x1a\n"
    assert b1[:8] == b"\x89PNG\r\n\x1a\n"
    # print md5s (useful when running locally)
    print('md5s:', hashlib.md5(b0).hexdigest(), hashlib.md5(b1).hexdigest())
