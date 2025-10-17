from core.util.loader import load_module_from_path
from core.engine.impl import Engine


def test_attractor_handle_drag_updates_position():
    mod = load_module_from_path('examples/Nature of Code/chapter02/Example_2_06_Attraction/Example_2_06_Attraction.py')
    eng = Engine(sketch_module=mod, headless=True)
    # run setup
    eng.run_frames(1)
    sk = eng.sketch
    attr = getattr(sk, 'attractor')
    # sanity
    assert hasattr(attr, 'position')
    # simulate pressing and set drag offset
    attr.handle_press(attr.position.x, attr.position.y)
    assert attr.dragging is True
    attr.drag_offset.x = 5.0
    attr.drag_offset.y = -3.0
    # perform drag
    mx = attr.position.x + 10.0
    my = attr.position.y + 20.0
    # call handle_drag which should update attr.position
    old_x, old_y = attr.position.x, attr.position.y
    attr.handle_drag(mx, my)
    assert attr.position.x != old_x or attr.position.y != old_y
    # ensure the new position matches mx + drag_offset
    assert abs(attr.position.x - (mx + 5.0)) < 1e-6
    assert abs(attr.position.y - (my - 3.0)) < 1e-6
