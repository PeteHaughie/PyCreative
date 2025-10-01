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


def test_mouse_pos_delegates_to_pygame():
    pygame = _init_pygame_dummy()

    from pycreative.app import Sketch

    # monkeypatch pygame.mouse.get_pos
    orig = pygame.mouse.get_pos

    def _fake():
        return (42, 99)

    pygame.mouse.get_pos = _fake

    s = Sketch()
    pos = s.mouse_pos()
    assert pos == (42, 99)
    assert s.mouse_x == 42
    assert s.mouse_y == 99

    # restore
    pygame.mouse.get_pos = orig
    pygame.quit()
