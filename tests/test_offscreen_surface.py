from pycreative.graphics import OffscreenSurface

import pygame
import os
import sys

# ensure src/ on path for tests
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_offscreen_draw_and_blit():
    # initialize headless display
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    main = pygame.Surface((100, 100))
    off = pygame.Surface((50, 50), flags=pygame.SRCALPHA)
    offsurf = OffscreenSurface(off)

    # draw a filled rect on offscreen
    offsurf.fill((255, 0, 0))
    offsurf.rect(0, 0, 50, 50)

    # ensure main surface is different
    before = main.get_at((10, 10))

    # blit offscreen onto main (note: pygame.Surface.blit(target, dest) expects
    # the source surface as the first argument when called on the target)
    main.blit(offsurf.raw, (10, 10))

    after = main.get_at((10, 10))

    assert before != after
    pygame.quit()
