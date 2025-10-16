from core.engine import Engine


def test_point_records_point_and_forwards_state():
    engine = Engine(headless=True)

    def draw(this):
        this.fill(10, 20, 30)
        this.stroke(40, 50, 60)
        this.stroke_weight(2)
        this.point(7, 13)

    engine.sketch = type('M', (), {'draw': draw})
    engine._normalize_sketch()
    engine.run_frames(1)

    pts = [c for c in engine.graphics.commands if c['op'] == 'point']
    assert len(pts) == 1
    args = pts[0].get('args', {})
    assert args.get('x') == 7 and args.get('y') == 13
    # engine state should reflect the last fill/stroke/stroke_weight calls
    assert engine.fill_color == (10, 20, 30)
    assert engine.stroke_color == (40, 50, 60)
    assert engine.stroke_weight == 2


def test_point_available_on_simple_api():
    engine = Engine(headless=True)
    this = engine and None
    # SimpleSketchAPI usage via direct creation
    from core.engine.api import SimpleSketchAPI
    api = SimpleSketchAPI(engine)
    api.point(1, 2)
    pts = [c for c in engine.graphics.commands if c['op'] == 'point']
    assert len(pts) == 1
    assert pts[0]['args']['x'] == 1 and pts[0]['args']['y'] == 2
