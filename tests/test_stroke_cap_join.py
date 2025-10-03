import pygame
from pycreative.app import Sketch
from pycreative.graphics import OffscreenSurface, Surface


def test_pending_stroke_cap_and_join_applied_to_offscreen():
    s = Sketch()
    # set pending values before any surface exists
    s.stroke_cap = 'round'
    s.stroke_join = 'bevel'
    off = s.create_graphics(64, 64, inherit_state=True)
    assert isinstance(off, OffscreenSurface)
    assert getattr(off, '_line_cap', None) == 'round'
    assert getattr(off, '_line_join', None) == 'bevel'


def test_setting_stroke_cap_applies_to_live_surface():
    # create a lightweight pygame.Surface and wrap in Graphics Surface
    pygame.init()
    raw = pygame.Surface((10, 10))
    gs = Surface(raw)
    s = Sketch()
    s.surface = gs
    s.stroke_cap = 'square'
    assert getattr(s.surface, '_line_cap', None) == 'square'
    s.stroke_join = 'round'
    assert getattr(s.surface, '_line_join', None) == 'round'
    pygame.quit()
