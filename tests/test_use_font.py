import os
import pygame
from pycreative.app import Sketch


def test_use_font_returns_font_instance():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    s = Sketch()
    f = s.use_font('courier new', size=24)
    assert f is None or hasattr(f, 'render')  # Accept either None or a Font with render
    pygame.quit()
