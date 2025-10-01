"""Run this example to see shape modes: POINTS, LINES, TRIANGLES, QUADS.

Usage: python examples/shape_modes_example.py
"""
# import pygame
# from pycreative.graphics import Surface


# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((640, 360))
#     surf = Surface(screen)

#     clock = pygame.time.Clock()
#     running = True
#     while running:
#         for ev in pygame.event.get():
#             if ev.type == pygame.QUIT:
#                 running = False

#         screen.fill((10, 10, 10))

#         # points
#         surf.stroke((255, 100, 100))
#         surf.stroke_weight(6)
#         surf.begin_shape('POINTS')
#         surf.vertex(80, 60)
#         surf.vertex(120, 80)
#         surf.vertex(160, 60)
#         surf.end_shape()

#         # lines
#         surf.stroke((100, 255, 100))
#         surf.stroke_weight(4)
#         surf.begin_shape('LINES')
#         surf.vertex(220, 40)
#         surf.vertex(380, 40)
#         surf.vertex(220, 80)
#         surf.vertex(380, 80)
#         surf.end_shape()

#         # triangle fan (a simple roof)
#         surf.fill((100, 100, 255))
#         surf.begin_shape('TRIANGLE_FAN')
#         surf.vertex(480, 40)
#         surf.vertex(440, 100)
#         surf.vertex(520, 100)
#         surf.vertex(560, 60)
#         surf.end_shape()

#         # quad
#         surf.fill((255, 200, 100))
#         surf.begin_shape('QUADS')
#         surf.vertex(80, 180)
#         surf.vertex(200, 180)
#         surf.vertex(200, 260)
#         surf.vertex(80, 260)
#         surf.end_shape()

#         pygame.display.flip()
#         clock.tick(30)

#     pygame.quit()


# if __name__ == '__main__':
#     main()


from pycreative.app import Sketch


class ShapeModesExample(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Shape Modes Example")
        self.no_loop()  # draw once

    def draw(self):
        self.clear((10, 10, 10))

        # points
        self.stroke((255, 100, 100))
        self.stroke_weight(6)
        self.begin_shape('POINTS')
        self.vertex(80, 60)
        self.vertex(120, 80)
        self.vertex(160, 60)
        self.end_shape()

        # lines
        self.stroke((100, 255, 100))
        self.stroke_weight(4)
        self.begin_shape('LINES')
        self.vertex(220, 40)
        self.vertex(380, 40)
        self.vertex(220, 80)
        self.vertex(380, 80)
        self.end_shape()

        # triangle fan (a simple roof)
        self.fill((100, 100, 255))
        self.begin_shape('TRIANGLE_FAN')
        self.vertex(480, 40)
        self.vertex(440, 100)
        self.vertex(520, 100)
        self.vertex(560, 60)
        self.end_shape()

        # quad
        self.fill((255, 200, 100))
        self.begin_shape('QUADS')
        self.vertex(80, 180)
        self.vertex(200, 180)
        self.vertex(200, 260)
        self.vertex(80, 260)
        self.end_shape()
