import pygame
from importlib import util


def load_example():
    spec = util.spec_from_file_location('sketch_mod', 'examples/Generative Gestaltung/01_P/P_1_2_2_01/P_1_2_2_01.py')
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cls = getattr(mod, 'P_1_2_2_01')
    return cls()


def test_sketch_color_helpers_and_hsb_draw(monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    inst = load_example()
    pygame.init()
    from pycreative.graphics import OffscreenSurface

    base = pygame.Surface((100, 100))
    off = OffscreenSurface(base)
    inst.surface = off
    # minimal setup
    inst.setup()

    # test RGB helpers
    c = (200, 10, 5)
    assert inst.red(c) == 200
    assert inst.green(c) == 10
    assert inst.blue(c) == 5

    # test hue/sat/brightness on simple color
    h = inst.hue((255, 0, 0))
    assert abs(h - 0) <= 2

    # test passing an HSB tuple into ellipse stroke doesn't crash
    inst.color_mode('HSB', 360, 100, 100)
    inst.no_stroke()
    inst.ellipse(10, 10, 20, 20, fill=None, stroke=(180, 50, 50))
    # ensure some pixel changed near the ellipse center
    px = inst.surface.get_pixel(10, 10)
    assert isinstance(px, tuple)
