"""Small utility helpers for PyCreative.

This module provides a Processing-like `size()` helper that wraps Python's
`len()` for sized objects, and a tiny `IntList` convenience wrapper that adds
a `.size()` method (mirroring Processing's IntList.size()).

Keep this module minimal: it intentionally avoids heavy dependencies and uses
duck-typing for objects that implement `__len__`.
"""
from typing import Any, Tuple

__all__ = ["size", "IntList"]


def size(obj: Any) -> int:
    """Return the length of `obj`, mirroring Processing's size() behavior for collections.

    Raises a TypeError if the object does not define `__len__`.
    """
    if hasattr(obj, "__len__"):
        return len(obj)
    raise TypeError(f"object of type {type(obj)!r} has no len()")


class IntList(list):
    """A tiny list[int] wrapper that exposes a `.size()` method.

    Use when you want Processing-like `.size()` semantics while still getting
    full list behavior (append, pop, iteration, etc.).
    """

    def size(self) -> int:
        return len(self)


def has_alpha(color: object) -> bool:
    """Return True if `color` looks like an (r,g,b,a) tuple with alpha != 255."""
    return isinstance(color, tuple) and len(color) == 4 and color[3] != 255


def draw_alpha_polygon_on_temp(surface_surf: Any, temp_surf: Any, points: list[tuple[float, float]], color: Tuple[int, ...], dest_x: int, dest_y: int) -> None:
    """Draw a polygon on a temporary surface and blit it to `surface_surf`.

    The function imports pygame lazily so importing this module doesn't require
    pygame to be installed at import-time.
    """
    import pygame

    rel_pts = [(int(round(px)), int(round(py))) for px, py in points]
    pygame.draw.polygon(temp_surf, color, rel_pts)
    surface_surf.blit(temp_surf, (dest_x, dest_y))


def draw_alpha_rect_on_temp(surface_surf: Any, temp_surf: Any, rect: Any, color: Tuple[int, ...]) -> None:
    """Draw a rect on a temporary surface and blit it to `surface_surf`.

    `rect` is expected to be a pygame.Rect-like object with width/height/left/top
    attributes. We import pygame lazily to avoid hard runtime dependency at import-time.
    """
    import pygame

    pygame.draw.rect(temp_surf, color, pygame.Rect(0, 0, rect.width, rect.height))
    surface_surf.blit(temp_surf, (rect.left, rect.top))

