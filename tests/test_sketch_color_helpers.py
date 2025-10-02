import pygame
import pytest

from pycreative.app import Sketch


def test_sketch_color_helpers_and_hsb_draw(monkeypatch):
    # Run headless
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    pygame.init()

    from pycreative.graphics import OffscreenSurface

    class MinimalSketch(Sketch):
        def setup(self):
            # use size to set any pending state if needed
            self.size(100, 100)

    inst = MinimalSketch()
    # construct offscreen surface and attach
    base = pygame.Surface((100, 100))
    off = OffscreenSurface(base)
    inst.surface = off
    inst.setup()

    # test RGB helpers
    c = (200, 10, 5)
    assert inst.red(c) == 200
    assert inst.green(c) == 10
    assert inst.blue(c) == 5

    # test hue on simple color (red)
    h = inst.hue((255, 0, 0))
    assert abs(h - 0) <= 2

    # test passing an HSB tuple into ellipse stroke doesn't crash
    inst.color_mode('HSB', 360, 100, 100)
    inst.no_stroke()
    # should not raise
    inst.ellipse(10, 10, 20, 20, fill=None, stroke=(180, 50, 50))
    # ensure get_pixel returns a tuple (we don't assert a color value here)
    px = inst.surface.get_pixel(10, 10)
    assert isinstance(px, tuple)
