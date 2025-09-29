import os
import pygame

from pycreative.graphics import OffscreenSurface


def test_per_call_fill_and_stroke_overrides():
    # Ensure headless mode for CI / local headless runs
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()

    # Create a raw pygame Surface and wrap it
    raw = pygame.Surface((100, 60))
    surf = OffscreenSurface(raw)

    # Global state on surface
    surf.fill((200, 200, 200))
    surf.stroke((0, 0, 0))
    surf.stroke_weight(1)

    # Draw a rectangle using per-call fill override (blue)
    surf.rect(10, 10, 30, 20, fill=(0, 0, 255), stroke=None)

    # Draw an ellipse with per-call stroke override (red) and no fill
    surf.ellipse(60, 30, 30, 20, fill=None, stroke=(255, 0, 0), stroke_weight=3)

    # Grab pixel arrays to assert approximate colors
    arr = pygame.surfarray.array3d(surf.raw)

    # Check center of the rectangle area -> should be blue
    rx, ry = 10 + 15, 10 + 10
    rcol = tuple(int(c) for c in arr[rx, ry])
    assert rcol[2] > 200 and rcol[0] < 100

    # Check pixel near ellipse edge -> should contain red in at least one channel
    ex, ey = 60, 30
    ecol = tuple(int(c) for c in arr[ex, ey])
    # since ellipse stroke may be thin, allow small tolerance
    assert ecol[0] > 150

    pygame.quit()
