import os
import pygame

from pycreative.app import Sketch


def test_pending_font_applied_after_run():
    """If a sketch requests a font before display creation (use_font),
    after run()/initialize the surface should have the concrete font when
    one was resolvable.
    """
    # Use dummy video driver for headless CI environments
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    # initialize pygame explicitly to ensure font subsystem is available
    pygame.init()

    s = Sketch()
    # Request a common system family before the display exists
    s.use_font("courier new", size=24)

    # Run one frame to allow pending state to be applied during initialize/run
    s.run(max_frames=1)

    try:
        # If the sketch resolved a concrete pygame.font.Font earlier, it
        # should be exposed as _loaded_font and the surface should have the
        # same active font instance.
        lf = getattr(s, "_loaded_font", None)
        if lf is not None:
            assert s.surface is not None
            assert getattr(s.surface, "_active_font", None) is not None
            assert s.surface._active_font is lf
    finally:
        pygame.quit()
