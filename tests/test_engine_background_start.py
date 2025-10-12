import time


def test_engine_background_start_and_stop():
    from src.core.engine import Engine

    calls = {'draw': 0}

    class Sketch:
        def draw(self):
            calls['draw'] += 1
            return []

    e = Engine()
    e._sketch = Sketch()

    # Start in background for 2 frames
    e.start(max_frames=2, background=True)

    # Wait briefly for background thread to finish (it should run quickly)
    timeout = 2.0
    t0 = time.time()
    while e.running and (time.time() - t0) < timeout:
        time.sleep(0.01)

    assert calls['draw'] == 2
    assert not e.running
