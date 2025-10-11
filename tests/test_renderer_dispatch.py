from src.core.renderer import Renderer


def test_renderer_dispatches_to_adapter():
    calls = []

    class FakeAdapter:
        def draw_circle(self, x, y, r, color=None, stroke=1):
            calls.append(('draw_circle', x, y, r, color, stroke))

        def draw_rect(self, x, y, w, h, color=None, stroke=1):
            calls.append(('draw_rect', x, y, w, h, color, stroke))

    adapter = FakeAdapter()
    r = Renderer(adapter)

    descriptors = [
        {'type': 'circle', 'args': {'x': 10, 'y': 20, 'r': 5, 'color': 'red', 'stroke': 2}},
        {'type': 'rect', 'args': {'x': 0, 'y': 0, 'w': 100, 'h': 50, 'color': 'blue'}},
    ]

    r.render(descriptors)

    assert calls == [
        ('draw_circle', 10, 20, 5, 'red', 2),
        ('draw_rect', 0, 0, 100, 50, 'blue', 1),
    ]
