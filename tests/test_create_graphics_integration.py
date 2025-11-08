def test_create_graphics_from_simple_api():
    """Ensure create_graphics is available on SimpleSketchAPI and records ops."""
    from core.engine.impl import Engine

    # Create a headless engine and call SimpleSketchAPI.create_graphics
    eng = Engine(sketch_module=None, headless=True)
    api = eng.api

    # Get the SimpleSketchAPI facade
    from core.engine.api.simple import SimpleSketchAPI

    s = SimpleSketchAPI(eng)
    pg = s.create_graphics(40, 30)
    assert pg is not None
    # begin and draw a rectangle
    pg.begin_draw()
    pg.fill(10)
    pg.rect(5, 5, 10, 10)
    pg.end_draw()

    # Engine graphics recorder should have an 'offscreen' op recorded
    rec = getattr(eng, 'graphics', None)
    assert rec is not None
    ops = [c for c in rec.commands if c.get('op') == 'offscreen']
    assert len(ops) >= 1
