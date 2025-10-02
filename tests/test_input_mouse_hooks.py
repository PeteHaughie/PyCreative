import pygame

from pycreative.app import Sketch
from pycreative import input as input_mod


class SketchMouseHooks(Sketch):
    # Avoid defining __init__ on pytest-collected test classes; pytest
    # warns when test classes define __init__ because it interferes with
    # collection/fixture semantics. Initialize per-test state in setup().

    import pygame
    import pytest

    from pycreative.app import Sketch
    from pycreative import input as input_mod


    class SketchMouseHooks(Sketch):
        """Helper Sketch subclass used by tests. Kept non-Test prefixed so pytest
        won't attempt to collect it as a test container.
        """
        def setup(self):
            # ensure setup can be called
            self.size(100, 100)
            # initialize runtime test flags here (per pytest's expectations)
            self.pressed = False
            self.released = False

        def on_event(self, event):
            # on_event should be called for mouse events
            if event.type == "mouse":
                assert getattr(event, "pos", None) is not None

        def mouse_pressed(self):
            self.pressed = True

        def mouse_released(self):
            self.released = True


    @pytest.fixture
    def sketch(monkeypatch):
        # use dummy video driver for headless tests
        monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
        pygame.init()
        s = SketchMouseHooks()
        s.setup()
        return s


    def test_mouse_pressed_and_released_are_forwarded(sketch):
        down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (10, 20), "button": 1})
        up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (10, 20), "button": 1})

        input_mod.dispatch_event(sketch, down)
        input_mod.dispatch_event(sketch, up)

        assert sketch.pressed is True
        assert sketch.released is True
