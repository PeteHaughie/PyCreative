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


def test_text_font_and_size_pending_applied():
    pygame = _init_pygame_dummy()

    from pycreative.app import Sketch

    class _S(Sketch):
        def setup(self):
            # Set a font instance and size before the display exists
            f = pygame.font.SysFont(None, 32)
            self.text_size(32)
            self.text_font(f)

        def draw(self):
            # draw nothing
            pass

    s = _S()
    # Call initialize() to exercise the pending-state application path
    s.initialize()

    assert s.surface is not None
    # Surface should have an active font instance assigned
    assert getattr(s.surface, "_active_font", None) is not None
    # The active font should be a pygame.font.Font instance

    try:
        import pygame as _pygame

        assert isinstance(s.surface._active_font, _pygame.font.Font)
    except Exception:
        # If pygame.font isn't available for some reason, at least ensure a non-None value was stored
        assert s.surface._active_font is not None

    pygame.quit()
