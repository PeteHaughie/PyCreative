"""
Test for pycreative.app.Sketch main loop (headless, 3 frames).
"""

from pycreative import Sketch


def test_sketch_runs_3_frames(monkeypatch):
    frames = []

    class TestSketch(Sketch):
        def setup(self):
            self.size(100, 100)

        def draw(self):
            frames.append(self.frame_count)

    # Monkeypatch pygame to avoid opening a window
    import pygame

    monkeypatch.setattr(
        pygame.display, "set_mode", lambda *a, **kw: pygame.Surface((100, 100))
    )
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(pygame, "init", lambda: None)
    monkeypatch.setattr(pygame, "quit", lambda: None)
    monkeypatch.setattr(
        pygame.time,
        "Clock",
        lambda: type("Clock", (), {"tick": lambda self, fps=0: 16})(),
    )
    monkeypatch.setattr(pygame.event, "get", lambda: [])
    monkeypatch.setattr(pygame.event, "pump", lambda: None)
    sketch = TestSketch()
    sketch.run(max_frames=3)
    assert frames == [1, 2, 3]
