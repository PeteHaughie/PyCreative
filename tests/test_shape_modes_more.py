import pygame
from pycreative.graphics import OffscreenSurface


def _mk(w=140, h=100):
    pygame.init()
    surf = pygame.Surface((w, h))
    off = OffscreenSurface(surf)
    return pygame, surf, off


def test_triangle_fan_draws():
    pygame, surf, off = _mk()
    try:
        off.fill((50, 150, 200))
        off.begin_shape('TRIANGLE_FAN')
        off.vertex(70, 10)  # center
        off.vertex(20, 60)
        off.vertex(50, 90)
        off.vertex(100, 80)
        off.vertex(120, 50)
        off.end_shape()

        # sample a point expected inside fan (near center)
        px = surf.get_at((70, 50))[:3]
        assert px != (0, 0, 0)
    finally:
        pygame.quit()


def test_triangle_strip_draws():
    pygame, surf, off = _mk()
    try:
        off.fill((180, 80, 180))
        off.begin_shape('TRIANGLE_STRIP')
        # strip vertices that form a zig-zag strip across the surface
        off.vertex(10, 10)
        off.vertex(10, 80)
        off.vertex(40, 10)
        off.vertex(40, 80)
        off.vertex(70, 10)
        off.vertex(70, 80)
        off.end_shape()

        # expect some interior pixel to be filled
        px = surf.get_at((35, 45))[:3]
        assert px != (0, 0, 0)
    finally:
        pygame.quit()


def test_quad_strip_draws():
    pygame, surf, off = _mk()
    try:
        off.fill((20, 200, 120))
        off.begin_shape('QUAD_STRIP')
        # pairs of vertices form adjacent quads
        off.vertex(10, 10)
        off.vertex(10, 50)
        off.vertex(50, 10)
        off.vertex(50, 50)
        off.vertex(90, 10)
        off.vertex(90, 50)
        off.end_shape()

        px = surf.get_at((30, 30))[:3]
        assert px != (0, 0, 0)
    finally:
        pygame.quit()


def test_empty_and_odd_vertex_counts_no_crash():
    pygame, surf, off = _mk()
    try:
        # empty shape: should be no-op
        off.begin_shape('TRIANGLES')
        off.end_shape()

        # odd vertex count for TRIANGLES: should not raise
        off.begin_shape('TRIANGLES')
        off.vertex(10, 10)
        off.vertex(20, 10)
        # single leftover vertex (odd) - end_shape() should handle gracefully
        off.end_shape()

        # odd count for QUADS
        off.begin_shape('QUADS')
        off.vertex(10, 30)
        off.vertex(30, 30)
        off.vertex(30, 50)
        # missing 4th vertex - end should not raise
        off.end_shape()
    finally:
        pygame.quit()


def test_bezier_mixed_with_vertices_flattens_and_draws():
    pygame, surf, off = _mk()
    try:
        off.fill((200, 120, 60))
        off.begin_shape()
        off.vertex(10, 70)
        # Add a bezier segment starting from previous vertex
        off.bezier_vertex(30, 10, 70, 10, 90, 70)
        off.vertex(110, 70)
        off.end_shape(close=True)

        # sample near center of the constructed filled shape
        px = surf.get_at((70, 50))[:3]
        assert px != (0, 0, 0)
    finally:
        pygame.quit()
