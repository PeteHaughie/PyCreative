import os
import pygame
import pytest

from pycreative.graphics import OffscreenSurface


def test_curve_point_endpoints_and_tangent():
    # numeric checks for curve_point and curve_tangent on a straight-line setup
    raw = pygame.Surface((1, 1))
    surf = OffscreenSurface(raw)

    p0 = (0.0, 0.0)
    p1 = (10.0, 0.0)
    p2 = (20.0, 0.0)
    p3 = (30.0, 0.0)

    cp0 = surf.curve_point(p0, p1, p2, p3, 0.0)
    cp1 = surf.curve_point(p0, p1, p2, p3, 1.0)
    assert cp0 == pytest.approx((10.0, 0.0))
    assert cp1 == pytest.approx((20.0, 0.0))

    # For a straight-line control set, tangent should be approximately (10,0)
    tan = surf.curve_tangent(p0, p1, p2, p3, 0.5)
    assert tan[0] == pytest.approx(10.0, rel=1e-2)
    assert tan[1] == pytest.approx(0.0, abs=1e-6)


def test_curve_rendering_pixels():
    # Headless-friendly rendering test that ensures curve() draws pixels
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()

    raw = pygame.Surface((120, 60))
    surf = OffscreenSurface(raw)

    # White background
    surf.clear((255, 255, 255))

    # Draw a red stroked curve
    surf.stroke((200, 0, 0))
    surf.stroke_weight(3)
    # points that form an arc-like curve
    x0, y0 = 10, 50
    x1, y1 = 30, 50
    x2, y2 = 60, 10
    x3, y3 = 90, 50
    surf.curve(x0, y0, x1, y1, x2, y2, x3, y3)

    arr = pygame.surfarray.array3d(surf.raw)
    # sample the curve midpoint (t=0.5)
    mx, my = surf.curve_point((x0, y0), (x1, y1), (x2, y2), (x3, y3), 0.5)
    sx, sy = int(mx), int(my)
    sx = max(0, min(sx, raw.get_width() - 1))
    sy = max(0, min(sy, raw.get_height() - 1))
    color = tuple(int(c) for c in arr[sx, sy])
    # Expect a strong red channel at the midpoint (stroke drawn)
    assert color[0] > 100

    pygame.quit()
