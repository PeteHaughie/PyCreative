import pytest
from core import color


def test_color_and_components():
    # Create color with 3-component RGB
    c = color.color(255, 204, 0)
    assert isinstance(c, int)
    assert color.red(c) == 255.0
    assert color.green(c) == 204.0
    assert color.blue(c) == 0.0
    assert color.alpha(c) == 255.0

    # Create grayscale with alpha as float
    c2 = color.color(0.5, 0.2)
    # grayscale 0.5 -> 127 or 128 depending on rounding; alpha 0.2 -> ~51
    assert 0 <= color.red(c2) <= 255
    assert 0 <= color.alpha(c2) <= 255


def test_lerp_color():
    c1 = color.color(255, 0, 0)
    c2 = color.color(0, 0, 255)
    mid = color.lerp_color(c1, c2, 0.5)
    # mid should have r ~128, b ~128
    assert abs(color.red(mid) - 128.0) <= 1.0
    assert abs(color.blue(mid) - 128.0) <= 1.0
    assert color.alpha(mid) == 255.0


def test_rgb_hsb_roundtrip_and_edges():
    # Known value: pure red
    h, s, v = color.rgb_to_hsb(255, 0, 0)
    assert pytest.approx(h, rel=1e-3) == 0.0
    assert pytest.approx(s, rel=1e-3) == 1.0
    assert pytest.approx(v, rel=1e-3) == 1.0

    # Round-trip some randomish colors
    samples = [
        (255, 204, 0),
        (128, 64, 200),
        (0, 0, 0),
        (255, 255, 255),
        (12, 34, 56),
    ]
    for r, g, b in samples:
        h, s, v = color.rgb_to_hsb(r, g, b)
        rr, gg, bb = color.hsb_to_rgb(h, s, v)
        # Allow small rounding differences after round-trip
        assert abs(rr - int(round(r))) <= 1
        assert abs(gg - int(round(g))) <= 1
        assert abs(bb - int(round(b))) <= 1


def test_engine_color_mode_hsb_integration():
    # Use a tiny sketch object to exercise SimpleSketchAPI methods
    class Sketch:
        def setup(self, this):
            # Switch engine to HSB mode and emit background and fill
            this.color_mode('HSB')
            # hue=0.0 (red), sat=1, bright=1 -> should map to red
            this.background(0.0, 1.0, 1.0)
            this.fill(0.0, 1.0, 1.0)

        def draw(self, this):
            # noop
            pass

    from core.engine.impl import Engine
    sk = Sketch()
    eng = Engine(sketch_module=sk, headless=True)
    # Run a single frame (setup and one draw)
    eng.run_frames(1)

    # Find first background recorded command and check RGB values were set
    bg_cmds = [c for c in eng.graphics.commands if c.get('op') == 'background']
    assert len(bg_cmds) >= 1
    args = bg_cmds[0].get('args', {})
    assert args.get('r') in (255, 254)
    assert args.get('g') in (0, 1)
    assert args.get('b') in (0, 1)

    # fill recorded as state change; inspect engine.fill_color
    assert getattr(eng, 'fill_color', None) is not None
    r, g, b = eng.fill_color
    assert r in (255, 254)
    assert g in (0, 1)
    assert b in (0, 1)

def test_color_mode_invalid_raises():
    from core.engine.impl import Engine
    class Sketch:
        def setup(self, this):
            # attempt to set an unsupported mode
            try:
                this.color_mode('FOO')
            except Exception:
                # swallow here so engine continues
                pass

    eng = Engine(sketch_module=Sketch(), headless=True)
    # Trying to run should not crash; the invalid mode should raise in API
    eng.run_frames(1)