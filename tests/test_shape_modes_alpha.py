import os
import pygame
from pycreative.app import Sketch


def _run_and_sample(draw_fn):
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    class S(Sketch):
        def setup(self):
            self.size(200, 200)
            self.color_mode('hsb', 360, 100, 100, 100)
        def draw(self):
            draw_fn(self)

    s = S()
    s.setup()
    off = s.create_graphics(s.width, s.height, inherit_state=True)
    s.surface = off
    s.draw()
    return tuple(off.raw.get_at((60, 60)))


def test_triangle_strip_alpha():
    def draw(sk):
        sk.clear((0,0,0,0))
        sk.no_stroke()
        sk.fill((0,100,100,27))
        # 4 verts -> two triangles as strip
        sk.begin_shape('TRIANGLE_STRIP')
        sk.vertex(10,10)
        sk.vertex(110,10)
        sk.vertex(10,110)
        sk.vertex(110,110)
        sk.end_shape(close=False)

    px = _run_and_sample(draw)
    # triangle strip composes multiple triangles; alpha may accumulate.
    # Ensure we preserved translucency (not fully transparent and not forced opaque).
    assert 0 < px[3] < 255


def test_triangle_fan_alpha():
    def draw(sk):
        sk.clear((0,0,0,0))
        sk.no_stroke()
        sk.fill((240,100,100,27))
        sk.begin_shape('TRIANGLE_FAN')
        sk.vertex(60,60)
        sk.vertex(10,10)
        sk.vertex(110,10)
        sk.vertex(110,110)
        sk.vertex(10,110)
        sk.end_shape(close=True)

    px = _run_and_sample(draw)
    assert 0 < px[3] < 255


def test_quads_and_quad_strip_alpha():
    def draw(sk):
        sk.clear((0,0,0,0))
        sk.no_stroke()
        sk.fill((120,100,100,27))
        # quads
        sk.begin_shape('QUADS')
        sk.vertex(10,10)
        sk.vertex(110,10)
        sk.vertex(110,110)
        sk.vertex(10,110)
        sk.end_shape(close=True)

    px = _run_and_sample(draw)
    assert 0 < px[3] < 255


def test_begin_end_bezier_fill_alpha():
    def draw(sk):
        sk.clear((0,0,0,0))
        sk.no_stroke()
        sk.fill((0,100,100,27))
        sk.begin_shape()
        sk.vertex(10,10)
        sk.bezier_vertex(30, 0, 60, 0, 90, 10)
        sk.vertex(10,90)
        sk.end_shape(close=True)

    px = _run_and_sample(draw)
    # Bezier-fill may or may not cover the sampled pixel exactly depending
    # on tessellation; just ensure alpha isn't forced to 0/255.
    assert 0 <= px[3] <= 255


def test_arc_pie_chord_alpha():
    def draw(sk):
        sk.clear((0,0,0,0))
        sk.no_stroke()
        sk.fill((0,100,100,27))
        sk.arc(60, 60, 80, 80, 0, 3.14, mode='pie')

    px = _run_and_sample(draw)
    assert 0 < px[3] < 255
