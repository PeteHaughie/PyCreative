from __future__ import annotations

from typing import Tuple, Iterable
import pygame


def has_alpha(color: object) -> bool:
    """Return True if `color` looks like an (r,g,b,a) tuple with alpha != 255."""
    return isinstance(color, tuple) and len(color) == 4 and color[3] != 255


def bbox_of_points(points: Iterable[tuple[int, int]]) -> tuple[int, int, int, int]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def draw_alpha_polygon_on_temp(surface_surf: pygame.Surface, temp_surf: pygame.Surface, points: list[tuple[float, float]], color: Tuple[int, ...], dest_x: int, dest_y: int) -> None:
    rel_pts = [(int(round(px)), int(round(py))) for px, py in points]
    pygame.draw.polygon(temp_surf, color, rel_pts)
    surface_surf.blit(temp_surf, (dest_x, dest_y))


def draw_alpha_rect_on_temp(surface_surf: pygame.Surface, temp_surf: pygame.Surface, rect: pygame.Rect, color: Tuple[int, ...]) -> None:
    pygame.draw.rect(temp_surf, color, pygame.Rect(0, 0, rect.width, rect.height))
    surface_surf.blit(temp_surf, (rect.left, rect.top))
