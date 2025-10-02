import pygame

from pycreative.app import Sketch
from pycreative import input as input_mod


class TestSketchMouseHooks(Sketch):
    def __init__(self):
        super().__init__()
        self.pressed = False
        self.released = False

    def setup(self):
        # ensure setup can be called
        self.size(100, 100)

    def on_event(self, event):
        # on_event should be called for mouse events
        if event.type == "mouse":
            assert getattr(event, "pos", None) is not None

    def mouse_pressed(self):
        self.pressed = True

    def mouse_released(self):
        self.released = True


def test_mouse_pressed_and_released_are_forwarded(monkeypatch):
    pygame.init()
    s = TestSketchMouseHooks()
    s.setup()

    down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (10, 20), "button": 1})
    up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (10, 20), "button": 1})

    input_mod.dispatch_event(s, down)
    input_mod.dispatch_event(s, up)

    assert s.pressed is True
    assert s.released is True
