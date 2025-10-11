"""Adapter module for pygame.

All direct imports of `pygame` should live here. This module exposes a small
API to create display surfaces used by the Engine and examples. In test
environments where pygame may not be available, provide a lightweight fallback
object that mimics the parts of the pygame surface API the project uses.
"""
try:
    import pygame  # type: ignore
    _HAS_PYGAME = True
except Exception:  # pragma: no cover - environment-dependent
    pygame = None  # type: ignore
    _HAS_PYGAME = False


class _FakeSurface:
    def __init__(self, width: int, height: int):
        self._w = width
        self._h = height

    def get_size(self):
        return (self._w, self._h)

    # Minimal blit stub
    def blit(self, src, dest):
        return None


def create_display_surface(width: int = 640, height: int = 480):
    """Create a display surface. Uses pygame when available, otherwise returns a fake surface."""
    if _HAS_PYGAME and pygame is not None:
        pygame.display.init()
        flags = 0
        return pygame.display.set_mode((width, height), flags)
    return _FakeSurface(width, height)
