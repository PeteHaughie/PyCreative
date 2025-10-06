import pygame
from pycreative.app import Sketch


def test_image_mode_pending_applies_after_initialize():
    s = Sketch()
    # set pending before surface exists
    s.image_mode('CENTER')
    # initialize which creates the surface and should apply pending state
    s.initialize(debug=False)
    try:
        assert s.surface is not None
        assert s.surface.image_mode() == s.surface.MODE_CENTER
    finally:
        pygame.quit()
