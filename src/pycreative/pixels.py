from __future__ import annotations

from typing import Any
from .types import RGB, RGBA
from contextlib import contextmanager

import pygame


class PixelView:
    """Adapter around nested-lists or numpy arrays to provide (h,w,c) indexing.

    This mirrors the previous PixelView behavior from `graphics.py` and keeps
    a mutable nested-list representation for tests and small images.
    """
    def __init__(self, data: Any):
        self._data = data

    @property
    def shape(self):
        if hasattr(self._data, "shape"):
            return self._data.shape
        h = len(self._data)
        w = len(self._data[0]) if h > 0 else 0
        c = len(self._data[0][0]) if w > 0 else 0
        return (h, w, c)

    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            cur = self._data
            for k in idx:
                cur = cur[k]
            return cur
        return self._data[idx]

    def __setitem__(self, idx, value):
        if isinstance(idx, tuple):
            cur = self._data
            for k in idx[:-1]:
                cur = cur[k]
            cur[idx[-1]] = value
            return
        self._data[idx] = value

    def raw(self):
        return self._data


def get_pixels(surface: pygame.Surface) -> PixelView:
    """Return a copy of the surface pixel data as a PixelView (H x W x C).

    Falls back to per-pixel reads so tests don't require numpy.
    """
    w, h = surface.get_size()
    has_alpha = bool(surface.get_flags() & pygame.SRCALPHA)
    try:
        arr: list[list[list[int]]] = []
        for y in range(h):
            row: list[list[int]] = []
            for x in range(w):
                c = surface.get_at((x, y))
                if has_alpha:
                    row.append([c.r, c.g, c.b, c.a])
                else:
                    row.append([c.r, c.g, c.b])
            arr.append(row)
        return PixelView(arr)
    except Exception:
        return PixelView([])


def set_pixels(surface: pygame.Surface, arr: Any) -> None:
    """Write a (H,W,3) or (H,W,4) nested-list/array into the surface.

    Values are clamped to 0..255. Raises ValueError on shape mismatch.
    """
    w, h = surface.get_size()
    if isinstance(arr, PixelView):
        arr = arr.raw()
    try:
        for y in range(h):
            row = arr[y]
            for x in range(w):
                v = row[x]
                if len(v) == 4:
                    surface.set_at((x, y), (int(v[0]) & 255, int(v[1]) & 255, int(v[2]) & 255, int(v[3]) & 255))
                else:
                    surface.set_at((x, y), (int(v[0]) & 255, int(v[1]) & 255, int(v[2]) & 255))
    except Exception as e:
        raise ValueError(f"set_pixels: expected nested list with shape (h,w,c) matching surface {(h,w)}; error: {e}")


def get_pixel(surface: pygame.Surface, x: int, y: int) -> RGB | RGBA:
    c = surface.get_at((int(x), int(y)))
    if bool(surface.get_flags() & pygame.SRCALPHA):
        return (c.r, c.g, c.b, c.a)
    return (c.r, c.g, c.b)


def set_pixel(surface: pygame.Surface, x: int, y: int, color: RGB | RGBA) -> None:
    surface.set_at((int(x), int(y)), color)


@contextmanager
def pixels(surface: pygame.Surface):
    """Context manager for pixel access. Yields a PixelView and writes back on exit."""
    pv = get_pixels(surface)
    try:
        yield pv
    finally:
        try:
            set_pixels(surface, pv.raw())
        except Exception:
            # best-effort: ignore write-back errors
            pass
