from core.engine.impl import Engine


def _record_rect_with_mode(mode, args):
    # Create an Engine and call core.shape.rect directly after setting rect_mode
    eng = Engine(sketch_module=None, headless=True)
    eng.rect_mode = mode
    # Call the shape helper directly
    from core.shape import rect as _rect
    _rect(eng, *args)
    rects = [c for c in eng.graphics.commands if c.get('op') == 'rect']
    if rects:
        return rects[0]['args']
    return None


def test_rect_mode_corner_defaults():
    args = _record_rect_with_mode('CORNER', (10, 20, 30, 40))
    assert args is not None
    assert args['x'] == 10
    assert args['y'] == 20
    assert args['w'] == 30
    assert args['h'] == 40


def test_rect_mode_corners():
    args = _record_rect_with_mode('CORNERS', (10, 20, 40, 60))
    assert args is not None
    assert args['x'] == 10
    assert args['y'] == 20
    assert args['w'] == 30
    assert args['h'] == 40


def test_rect_mode_center():
    args = _record_rect_with_mode('CENTER', (50, 50, 20, 10))
    assert args is not None
    assert args['x'] == 40.0
    assert args['y'] == 45.0
    assert args['w'] == 20
    assert args['h'] == 10


def test_rect_mode_radius():
    args = _record_rect_with_mode('RADIUS', (50, 50, 10, 5))
    assert args is not None
    assert args['x'] == 40.0
    assert args['y'] == 45.0
    assert args['w'] == 20.0
    assert args['h'] == 10.0
