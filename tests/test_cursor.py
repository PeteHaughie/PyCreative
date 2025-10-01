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


def test_no_cursor_pending_and_applied():
    pygame = _init_pygame_dummy()

    from pycreative.app import Sketch

    class _S(Sketch):
        def setup(self):
            # call no_cursor before the display is created
            self.no_cursor()

        def draw(self):
            # nothing
            pass

    s = _S()
    # pending value should be set before run
    assert getattr(s, "_pending_cursor") is not None

    # Replace pygame.mouse.set_visible to capture calls made during run()
    orig_set_visible = pygame.mouse.set_visible
    visible_calls = []

    def _record(v):
        visible_calls.append(bool(v))
        # still call the original to keep pygame state consistent
        try:
            return orig_set_visible(v)
        except Exception:
            # ignore platform quirks
            return None

    pygame.mouse.set_visible = _record

    try:
        # run for a single frame to allow the display to be created and pending applied
        s.run(max_frames=1)
    finally:
        # restore original implementation (pygame may be quit by run())
        try:
            pygame.mouse.set_visible = orig_set_visible
        except Exception:
            pass

    # ensure our wrapper recorded a call to hide the cursor
    assert False in visible_calls

    pygame.quit()
