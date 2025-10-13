def test_custom_snapshot_backend_is_used(tmp_path):
    import importlib, sys
    sys.path.insert(0, 'src')

    calls = []

    def my_backend(path, w, h, engine):
        calls.append((path, w, h))
        # write a tiny file to satisfy expectations
        with open(path, 'wb') as f:
            f.write(b'PNG')

    class sketch:
        def draw(this):
            this.save_frame(str(tmp_path / 'out.png'))

    mod = importlib.import_module('core.engine')
    Engine = getattr(mod, 'Engine')
    eng = Engine(sketch_module=sketch, headless=True)
    eng.snapshot_backend = my_backend
    eng.run_frames(1)

    assert len(calls) == 1
    rec = [c for c in eng.graphics.commands if c['op'] == 'save_frame']
    assert rec and rec[0]['args']['backend'] == 'custom'


def test_default_snapshot_backend_records(tmp_path):
    import importlib, sys
    sys.path.insert(0, 'src')

    out = tmp_path / 'out.png'

    class sketch:
        def draw(this):
            this.save_frame(str(out))

    mod = importlib.import_module('core.engine')
    Engine = getattr(mod, 'Engine')
    eng = Engine(sketch_module=sketch, headless=True)
    eng.run_frames(1)

    rec = [c for c in eng.graphics.commands if c['op'] == 'save_frame']
    assert len(rec) == 1
    # backend may be 'pillow' if PIL is installed in env, otherwise 'none'
    assert rec[0]['args']['backend'] in ('pillow', 'none')
