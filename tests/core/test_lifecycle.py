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

    # Calling no_loop() in setup should still allow a single draw to run
    # (Processing semantics). Ensure exactly one draw occurs even if we
    # advance multiple frames.
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
    assert sketch.draws == 1


def test_no_loop_called_in_draw_stops_future_frames():
    """If a sketch calls no_loop() from inside draw(), that draw should
    complete but subsequent frames should be skipped.
    """
    import importlib, sys
    sys.path.insert(0, 'src')

    class sketch:
        draws = 0

        def draw(this):
            # on first draw, disable looping
            if sketch.draws == 0:
                this.no_loop()
            sketch.draws += 1

    mod = importlib.import_module('core.engine')
    Engine = getattr(mod, 'Engine')
    eng = Engine(sketch_module=sketch, headless=True)
    eng.run_frames(5)
    # Should have drawn exactly once (the draw that triggered no_loop())
    assert sketch.draws == 1


def test_loop_toggle_allows_resuming_loop():
    """Verify that calling loop() re-enables continuous drawing after a
    previous no_loop(). This simulates a sketch that disables looping in
    setup but then resumes looping (for example, in response to an event).
    """
    import importlib, sys
    sys.path.insert(0, 'src')

    class sketch:
        draws = 0

        def setup(this):
            # disable automatic looping initially
            this.no_loop()

        def draw(this):
            sketch.draws += 1
            # after the one-shot draw, re-enable looping so subsequent
            # frames in the same run will continue drawing
            if sketch.draws == 1:
                this.loop()

    mod = importlib.import_module('core.engine')
    Engine = getattr(mod, 'Engine')
    eng = Engine(sketch_module=sketch, headless=True)
    eng.run_frames(4)
    # After re-enabling loop during the first draw, remaining frames should draw
    assert sketch.draws >= 2


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
