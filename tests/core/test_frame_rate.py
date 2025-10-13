def test_default_frame_rate_and_api():
    import importlib, sys
    sys.path.insert(0, 'src')

    mod = importlib.import_module('core.engine')
    Engine = getattr(mod, 'Engine')

    # default frame rate should be 60
    eng = Engine(sketch_module=None, headless=True)
    assert eng.frame_rate == 60

    # frame_rate via API updates engine
    class sketch:
        def setup(this):
            this.frame_rate(30)
        def draw(this):
            pass

    eng2 = Engine(sketch_module=sketch, headless=True)
    eng2.run_frames(1)
    assert eng2.frame_rate == 30


def test_frame_rate_unrestricted():
    import importlib, sys
    sys.path.insert(0, 'src')

    mod = importlib.import_module('core.engine')
    Engine = getattr(mod, 'Engine')

    class sketch:
        def setup(this):
            this.frame_rate(-1)
        def draw(this):
            pass

    eng = Engine(sketch_module=sketch, headless=True)
    eng.run_frames(1)
    assert eng.frame_rate == -1
