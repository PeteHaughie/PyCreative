import time


def test_bootstrap_registers_headless_adapters_and_runs():
    from src.core.bootstrap import build_engine

    # Build engine in headless mode (no adapters provided)
    engine = build_engine(headless=True)

    # Should have draw and graphics adapters registered on the engine
    assert getattr(engine, '_draw_adapter', None) is not None
    assert getattr(engine, '_graphics_adapter', None) is not None

    # Attach a simple sketch and run background for a short time
    calls = {'draw': 0}

    class Sketch:
        def draw(self):
            calls['draw'] += 1
            return []

    engine._sketch = Sketch()

    # Start background indefinite run, then stop after a short delay
    engine.start(background=True)
    time.sleep(0.05)
    engine.stop()

    assert calls['draw'] > 0
