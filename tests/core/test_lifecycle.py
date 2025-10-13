def test_setup_runs_once():
    import importlib, sys
    sys.path.insert(0, 'src')

    class sketch:
        count = 0

        def setup():
            sketch.count += 1

        def draw(this):
            pass

    mod = importlib.import_module('core.engine')
    Engine = getattr(mod, 'Engine')
    eng = Engine(sketch_module=sketch, headless=True)
    eng.run_frames(3)
    assert sketch.count == 1


def test_no_loop_prevents_draw():
    import importlib, sys
    sys.path.insert(0, 'src')

    class sketch:
        draws = 0

        def draw(this):
            sketch.draws += 1

        def setup(this):
            this.no_loop()

    mod = importlib.import_module('core.engine')
    Engine = getattr(mod, 'Engine')
    eng = Engine(sketch_module=sketch, headless=True)
    eng.run_frames(3)
    # setup disables looping, so only one draw (the redraw semantics would
    # permit one draw if redraw requested; we didn't request redraw)
    assert sketch.draws == 0


def test_redraw_one_shot():
    import importlib, sys
    sys.path.insert(0, 'src')

    class sketch:
        draws = 0

        def draw(this):
            sketch.draws += 1

        def setup(this):
            this.no_loop()
            this.redraw()

    mod = importlib.import_module('core.engine')
    Engine = getattr(mod, 'Engine')
    eng = Engine(sketch_module=sketch, headless=True)
    eng.run_frames(1)
    # redraw requested in setup produces a single draw
    assert sketch.draws == 1


def test_save_frame_records_command(tmp_path):
    import importlib, sys
    sys.path.insert(0, 'src')

    out = tmp_path / 'frame.png'

    class sketch:
        def draw(this):
            this.save_frame(str(out))

    mod = importlib.import_module('core.engine')
    Engine = getattr(mod, 'Engine')
    eng = Engine(sketch_module=sketch, headless=True)
    eng.run_frames(1)

    # engine should have recorded a save_frame op
    found = [c for c in eng.graphics.commands if c['op'] == 'save_frame']
    assert len(found) == 1
    assert found[0]['args']['path'] == str(out)
