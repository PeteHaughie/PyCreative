import os
import pygame
from pycreative.app import Sketch


def test_translucent_triangles_offscreen(tmp_path):
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()

    class TriTest(Sketch):
        def setup(self):
            self.size(200, 200)
            self.color_mode('hsb', 360, 100, 100, 100)

        def draw(self):
            self.clear((0, 0, 0, 0))
            self.no_stroke()
            self.fill((0, 100, 100, 27))
            self.triangle(20, 20, 120, 20, 20, 120)
            self.fill((240, 100, 100, 27))
            self.triangle(60, 60, 180, 60, 60, 180)

    s = TriTest()
    s.setup()
    off = s.create_graphics(s.width, s.height, inherit_state=True)
    s.surface = off
    s.draw()

    # sample a pixel in the overlap area; expect stored alpha to be 69 (27/100*255)
    px = off.raw.get_at((80, 80))
    rgba = tuple(px)
    # alpha channel should be present and equal to scaled value (27/100 * 255 -> 69)
    assert rgba[3] == 69
