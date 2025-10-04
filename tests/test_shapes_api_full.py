import pygame
from pycreative.graphics import Surface as GraphicsSurface
from pycreative.app import Sketch


def test_all_shape_primitives_and_aliases_run_without_error():
    # Initialize pygame (no display required for Surface creation)
    pygame.init()
    try:
        raw = pygame.Surface((200, 200), flags=pygame.SRCALPHA)
        gs = GraphicsSurface(raw)

        # Surface-level primitives
        gs.clear((255, 255, 255))
        gs.fill((10, 20, 30))
        gs.stroke((0, 0, 0))
        gs.stroke_weight(2)
        gs.ellipse(50, 50, 40, 20)
        gs.circle(100, 50, 30)
        gs.rect(10, 10, 30, 20)
        gs.line(0, 0, 199, 199)
        gs.point(5, 5)
        gs.triangle(10, 10, 20, 30, 30, 10)
        gs.quad(40, 40, 60, 40, 60, 60, 40, 60)
        gs.arc(100, 100, 40, 20, 0, 3.14)
        gs.bezier_detail(5)
        gs.bezier(10, 150, 30, 130, 50, 170, 70, 150)

        # polygon and polyline helpers
        poly = [(10.0, 10.0), (50.0, 20.0), (30.0, 60.0)]
        gs.polygon_with_style(poly, fill=(1, 2, 3), stroke=(0, 0, 0))
        gs.polygon(poly)
        gs.polyline(poly)
        gs.polyline_with_style(poly, stroke=(0, 0, 0), stroke_weight=1)

        # begin/vertex/end shape (triangles)
        gs.begin_shape('TRIANGLES')
        gs.vertex(10, 10)
        gs.vertex(20, 40)
        gs.vertex(40, 10)
        gs.end_shape()

        # Bezier vertex path
        gs.begin_shape('TRIANGLE_FAN')
        gs.vertex(60, 60)
        gs.bezier_vertex(65, 65, 70, 70, 80, 60)
        gs.vertex(100, 100)
        gs.end_shape(close=True)

        # Now test the Sketch wrappers by attaching the GraphicsSurface
        sketch = Sketch()
        sketch.surface = gs
        sketch.size(200, 200)
        sketch.fill((123, 123, 123))
        sketch.ellipse(50, 50, 10, 20)
        sketch.circle(60, 60, 12)
        sketch.rect(10, 10, 20, 20)
        sketch.line(0, 0, 10, 10)
        sketch.triangle(0,0, 5,5, 10,0)
        sketch.quad(0,0, 10,0, 10,10, 0,10)
        sketch.point(15, 15)
        sketch.polyline([(1,1),(2,2),(3,1)])
        sketch.begin_shape('QUADS')
        sketch.vertex(5,5)
        sketch.vertex(10,5)
        sketch.vertex(10,10)
        sketch.vertex(5,10)
        sketch.end_shape(close=True)

        # If we reached here without exceptions the API is exercised.
        assert True
    finally:
        pygame.quit()
