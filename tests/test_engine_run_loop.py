def test_engine_run_loop_calls_draw_and_renders():
    from src.core.engine import Engine

    calls = {'draw': 0, 'rendered': []}

    class Sketch:
        def __init__(self):
            self.frames = 0

        def draw(self):
            self.frames += 1
            calls['draw'] += 1
            # Return a simple descriptor each frame
            return [{'type': 'rect', 'args': {'x': 0, 'y': 0, 'w': 1, 'h': 1}}]

    class FakeAdapter:
        def draw_rect(self, x, y, w, h, color=None, stroke=1):
            calls['rendered'].append(('rect', x, y, w, h))

    e = Engine()
    # Attach sketch directly for this test
    e._sketch = Sketch()

    # Register a fake draw adapter via API register so engine._draw_adapter is set
    class DrawAPI:
        def __init__(self, adapter):
            self.adapter = adapter

        def register_api(self, engine):
            engine._draw_adapter = self.adapter

    e.register_api(DrawAPI(FakeAdapter()))

    # Run for 3 frames
    e.run(3)

    assert calls['draw'] == 3
    assert len(calls['rendered']) == 3
