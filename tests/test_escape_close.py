import os
import sys
import pathlib

# Make local `src/` visible on sys.path so tests import the in-repo package
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))


def _init_pygame_dummy():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame

    pygame.init()
    return pygame


def test_escape_closes_by_default():
    pygame = _init_pygame_dummy()

    from pycreative.app import Sketch
    from pycreative import input as input_mod

    s = Sketch()
    s._running = True

    ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    input_mod.dispatch_event(s, ev)

    assert s._running is False

    pygame.quit()


def test_escape_respect_set_escape_closes():
    pygame = _init_pygame_dummy()

    from pycreative.app import Sketch
    from pycreative import input as input_mod

    s = Sketch()
    s.set_escape_closes(False)
    s._running = True

    ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    input_mod.dispatch_event(s, ev)

    # still running because the behavior was disabled
    assert s._running is True

    pygame.quit()
