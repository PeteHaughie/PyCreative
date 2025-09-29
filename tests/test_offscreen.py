import os
import sys
import pathlib

# Make local `src/` visible on sys.path so tests import the in-repo package
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))


def _init_pygame_dummy():
    # Use dummy video driver for headless test runs
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame

    pygame.init()
    return pygame


def test_create_graphics_inherits_style():
    pygame = _init_pygame_dummy()

    from pycreative.app import Sketch
    from pycreative.graphics import Surface as GraphicsSurface

    sk = Sketch()
    main_surf = pygame.Surface((200, 200), flags=pygame.SRCALPHA)
    gs = GraphicsSurface(main_surf)
    # set some style state
    gs.fill((10, 20, 30))
    gs.stroke((1, 2, 3))
    gs.stroke_weight(5)
    gs.set_line_cap("round")
    gs.set_line_join("round")

    # attach to sketch and create offscreen with inherit_state True
    sk.surface = gs
    off = sk.create_graphics(100, 100, inherit_state=True)

    assert off._fill == (10, 20, 30)
    assert off._stroke == (1, 2, 3)
    assert off._stroke_weight == 5
    assert off._line_cap == "round"
    assert off._line_join == "round"

    pygame.quit()


def test_offscreen_draw_primitives_no_errors_and_pixels_change():
    pygame = _init_pygame_dummy()

    from pycreative.graphics import OffscreenSurface

    surf = pygame.Surface((120, 120), flags=pygame.SRCALPHA)
    off = OffscreenSurface(surf)

    # Clear to black and draw shapes
    off.clear((0, 0, 0))
    off.rect(10, 10, 40, 40, fill=(255, 0, 0), stroke=(0, 255, 0), stroke_width=2)
    off.triangle(60, 10, 100, 10, 80, 50, fill=(0, 0, 255), stroke=(255, 255, 0), stroke_width=1)
    off.quad(10, 60, 50, 60, 50, 100, 10, 100, fill=(10, 10, 10), stroke=(255, 0, 255))
    off.ellipse(80, 80, 30, 20, fill=(0, 255, 255), stroke=(255, 0, 0))
    off.arc(60, 60, 30, 30, 0, 3.14, mode="pie", fill=(123, 123, 123))

    # Check a pixel well inside the rectangle we drew is red (the fill)
    px = surf.get_at((30, 30))
    assert px.r == 255 and px.g == 0

    # Check a pixel inside the triangle roughly (80,20)
    px_tri = surf.get_at((80, 20))
    # either blue fill or yellow stroke; just ensure it's not the cleared black
    assert (px_tri.r, px_tri.g, px_tri.b) != (0, 0, 0)

    # Ensure the img alias exists and is callable
    assert callable(getattr(off, "img", None))

    pygame.quit()
