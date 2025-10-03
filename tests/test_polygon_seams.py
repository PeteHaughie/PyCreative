import math
import pygame
from pycreative.graphics import Surface


def sample_missing_edges(width, height, mouse_x, mouse_y, stroke_alpha=25, tol=8):
    pygame.init()
    W, H = width, height
    circle_resolution = int(2 + (mouse_y + 100) * 8.0 / H)
    radius = mouse_x - W / 2 + 0.5
    angle = (2 * math.pi) / circle_resolution

    raw = pygame.Surface((W, H))
    raw.fill((255, 255, 255))
    surf = Surface(raw)
    surf.no_fill()
    surf.stroke((0, 0, 0, stroke_alpha))
    surf.stroke_weight(2)
    surf.translate(W / 2, H / 2)

    pts = []
    surf.begin_shape()
    for i in range(circle_resolution + 1):
        x = 0 + math.cos(angle * i) * radius
        y = 0 + math.sin(angle * i) * radius
        pts.append((W / 2 + x, H / 2 + y))
        surf.vertex(x, y)
    surf.end_shape()

    # sample along edges
    bg = (255, 255, 255)
    missing = []
    N = circle_resolution
    for i in range(N):
        a = pts[i]
        b = pts[(i + 1) % N]
        found = False
        for t in (0.15, 0.3, 0.5, 0.7, 0.85):
            sx = int(round(a[0] + (b[0] - a[0]) * t))
            sy = int(round(a[1] + (b[1] - a[1]) * t))
            if sx < 0 or sx >= W or sy < 0 or sy >= H:
                continue
            px = raw.get_at((sx, sy))[:3]
            if any(abs(int(px[c]) - bg[c]) > tol for c in range(3)):
                found = True
                break
        if not found:
            missing.append(i)
    return missing


def test_repro_244_398_has_no_missing_edges():
    missing = sample_missing_edges(720, 720, 244, 398)
    assert missing == [], f"Found missing edges: {missing}"
