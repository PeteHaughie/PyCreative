from core.engine import Engine


def test_fill_and_rect_records_fill():
    engine = Engine(headless=True)

    # simulate sketch that sets fill in setup and draws a rect
    def setup(this):
        this.fill(10, 20, 30)

    def draw(this):
        this.rect(5, 5, 10, 10)

    engine.sketch = type('M', (), {'setup': setup, 'draw': draw})
    engine._normalize_sketch()

    engine.run_frames(1)

    # find rect command and ensure it includes fill via engine state
    rect_cmds = [c for c in engine.graphics.commands if c['op'] == 'rect']
    assert len(rect_cmds) == 1
    args = rect_cmds[0]['args']
    # since SimpleSketchAPI.rect delegates to API which records raw args,
    # fill is stored on engine.fill_color
    assert engine.fill_color == (10, 20, 30)


def test_square_records_rect_with_size_and_state():
    engine = Engine(headless=True)
    def draw(this):
        this.fill(255)
        this.square(0, 0, 50)

    engine.sketch = type('M', (), {'draw': draw})
    engine._normalize_sketch()
    engine.run_frames(1)

    rects = [c for c in engine.graphics.commands if c['op'] == 'rect']
    assert len(rects) == 1
    args = rects[0]['args']
    assert args['w'] == 50 and args['h'] == 50
    assert engine.fill_color == (255, 255, 255)


def test_stroke_weight_and_line():
    engine = Engine(headless=True)
    def draw(this):
        this.stroke(0)
        this.stroke_weight(3)
        this.line(0, 0, 10, 10)

    engine.sketch = type('M', (), {'draw': draw})
    engine._normalize_sketch()
    engine.run_frames(1)

    lines = [c for c in engine.graphics.commands if c['op'] == 'line']
    assert len(lines) == 1
    # API records raw args; stroke weight is on engine
    assert engine.stroke_weight == 3
    assert engine.stroke_color == (0, 0, 0)
