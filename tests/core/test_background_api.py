from core.engine import Engine


def test_background_rgb_records_color():
    eng = Engine(headless=True)
    def draw(this):
        this.background(10, 20, 30)
    eng.sketch = type('M', (), {'draw': draw})
    eng._normalize_sketch()
    eng.run_frames(1)

    # background should be recorded
    bgs = [c for c in eng.graphics.commands if c['op'] == 'background']
    assert len(bgs) >= 1
    assert bgs[-1]['args'] == {'r': 10, 'g': 20, 'b': 30}
    assert eng.background_color == (10, 20, 30)


def test_background_hsb_converts_to_rgb():
    eng = Engine(headless=True)
    eng.color_mode = 'HSB'

    # pure red in HSB is hue=0, sat=255, bright=255 (using 0-255 convention)
    def draw(this):
        this.background(0, 255, 255)

    eng.sketch = type('M', (), {'draw': draw})
    eng._normalize_sketch()
    eng.run_frames(1)

    bgs = [c for c in eng.graphics.commands if c['op'] == 'background']
    assert len(bgs) >= 1
    # converted to RGB should be red (255,0,0)
    assert eng.background_color == (255, 0, 0)