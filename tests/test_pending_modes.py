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


def test_rect_mode_set_in_setup_applies_after_run():
    pygame = _init_pygame_dummy()

    from pycreative.app import Sketch

    class _S(Sketch):
        def setup(self):
            # set rect mode before display exists
            self.rect_mode('CENTER')

        def draw(self):
            # nothing
            pass

    s = _S()
    # run a single frame to initialize display and apply pending modes
    s.run(max_frames=1)

    # underlying surface should now have CENTER rect mode
    assert s.surface is not None
    assert s.surface._rect_mode == s.surface.MODE_CENTER

    pygame.quit()
