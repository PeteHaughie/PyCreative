import pygame

from pycreative.app import Sketch


class SeedSketch(Sketch):
    def __init__(self, sketch_path=None, seed=None):
        super().__init__(sketch_path=sketch_path, seed=seed)
        self.w = 64
        self.h = 48

    def setup(self):
        # small canvas for quick tests
        self.size(self.w, self.h)

    def draw(self):
        # draw some random rectangles using self.random()
        self.surface.clear((0, 0, 0))
        for i in range(10):
            x = int(self.random(0, self.w))
            y = int(self.random(0, self.h))
            w = int(self.random(1, 16))
            h = int(self.random(1, 16))
            r = int(self.random(0, 255))
            g = int(self.random(0, 255))
            b = int(self.random(0, 255))
            self.surface.rect(x, y, w, h, fill=(r, g, b))


def sample_pixels(surf):
    # sample a few deterministic coords
    coords = [(0, 0), (5, 5), (10, 10), (20, 7), (30, 12), (40, 20), (50, 30)]
    out = []
    for x, y in coords:
        try:
            col = surf.get(x, y)
            out.append(tuple(col))
        except Exception:
            out.append(None)
    return out


def test_random_seed_constructor_reproducible(monkeypatch):
    # ensure pygame can create surfaces in headless mode
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    pygame.init()

    s1 = SeedSketch(seed=12345)
    # create an offscreen surface for s1 to draw into
    off1 = s1.create_graphics(s1.w, s1.h)
    # direct the sketch to draw into the offscreen surface
    s1.surface = off1
    # run draw once
    with off1:
        s1.draw()
    samples1 = sample_pixels(off1)

    s2 = SeedSketch(seed=12345)
    off2 = s2.create_graphics(s2.w, s2.h)
    s2.surface = off2
    with off2:
        s2.draw()
    samples2 = sample_pixels(off2)

    assert samples1 == samples2
