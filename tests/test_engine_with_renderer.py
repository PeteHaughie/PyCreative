from src.core.engine import Engine
from src.core.renderer import Renderer


def test_engine_uses_renderer_to_draw(monkeypatch):
    calls = []

    class FakeDrawAdapter:
        def draw_circle(self, x, y, r, color=None, stroke=1):
            calls.append(('draw_circle', x, y, r, color, stroke))

    class Sketch:
        def setup(self):
            pass

        def draw(self):
            # Return a list of descriptors for the renderer
            return [{'type': 'circle', 'args': {'x': 1, 'y': 2, 'r': 3, 'color': 'g'}}]

    engine = Engine()
    # Pretend the engine has a registered draw adapter via register_api
    adapter = FakeDrawAdapter()
    # Convention: register_api may set engine._draw_adapter; emulate that here
    engine._draw_adapter = adapter

    # Attach a sketch instance to the engine (minimal contract for tests)
    engine._sketch = Sketch()

    # Start engine for a single frame; expect renderer to call adapter
    engine.start(max_frames=1, headless=True)

    assert calls == [('draw_circle', 1, 2, 3, 'g', 1)]
