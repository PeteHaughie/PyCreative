import os
import pytest

from pycreative.app import Sketch
from pycreative.graphics import Surface as GraphicsSurface


def _init_pygame_dummy():
    # Use dummy video driver for headless test runs
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame as _pygame

    _pygame.init()
    return _pygame


def test_sketch_constants_and_mode_case_insensitive(tmp_path):
    s = Sketch()
    # constants exist and map to graphics constants
    assert hasattr(s, 'CENTER')
    assert hasattr(s, 'CORNER')
    assert s.CENTER == GraphicsSurface.MODE_CENTER
    assert s.CORNER == GraphicsSurface.MODE_CORNER

    # pending mode setters accept lowercase names
    s._pending_rect_mode = object()  # reset
    s.rect_mode('center')
    assert s._pending_rect_mode == GraphicsSurface.MODE_CENTER
    s.rect_mode('corner')
    assert s._pending_rect_mode == GraphicsSurface.MODE_CORNER

    s._pending_ellipse_mode = object()
    s.ellipse_mode('center')
    assert s._pending_ellipse_mode == GraphicsSurface.MODE_CENTER
    s.ellipse_mode('corner')
    assert s._pending_ellipse_mode == GraphicsSurface.MODE_CORNER


def test_surface_push_pop_aliases():
    # create a dummy pygame surface to construct GraphicsSurface
    pygame = _init_pygame_dummy()
    surf = pygame.Surface((10, 10))
    from pycreative.graphics import Surface as GraphicsSurface
    gs = GraphicsSurface(surf)

    # push_matrix/pop_matrix should mirror push/pop
    gs.push_matrix()
    # mutate top matrix and ensure pop_matrix restores
    import pygame

    from pycreative.app import Sketch
    from pycreative.graphics import Surface as GraphicsSurface


    def test_sketch_constants_and_mode_case_insensitive(tmp_path):
        s = Sketch()
        # constants exist and map to graphics constants
        assert hasattr(s, 'CENTER')
        assert hasattr(s, 'CORNER')
        assert s.CENTER == GraphicsSurface.MODE_CENTER
        assert s.CORNER == GraphicsSurface.MODE_CORNER

        # pending mode setters accept lowercase names
        s._pending_rect_mode = object()  # reset
        s.rect_mode('center')
        assert s._pending_rect_mode == GraphicsSurface.MODE_CENTER
        s.rect_mode('corner')
        assert s._pending_rect_mode == GraphicsSurface.MODE_CORNER

        s._pending_ellipse_mode = object()
        s.ellipse_mode('center')
        assert s._pending_ellipse_mode == GraphicsSurface.MODE_CENTER
        s.ellipse_mode('corner')
        assert s._pending_ellipse_mode == GraphicsSurface.MODE_CORNER


    def test_surface_push_pop_aliases():
        # create a dummy pygame surface to construct GraphicsSurface
        surf = pygame.Surface((10, 10))
        gs = GraphicsSurface(surf)

        # push_matrix/pop_matrix should mirror push/pop
        before = gs._current_matrix()
        gs.push_matrix()
        # mutate top matrix and ensure pop_matrix restores
        gs.translate(5, 7)
        assert gs._current_matrix() != before
        gs.pop_matrix()
        assert gs._current_matrix() == before

        # popping base should raise on Surface.pop() but alias should do same
        with pytest.raises(IndexError):
            # pop until base then pop again to trigger
            while True:
                gs.pop()