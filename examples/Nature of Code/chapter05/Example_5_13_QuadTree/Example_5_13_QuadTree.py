"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_13_QuadTree/Example_5_13_QuadTree.pde

// Daniel Shiffman
// http://codingtra.in
// http://patreon.com/codingtrain

// QuadTree
// 1: https://www.youtube.com/watch?v=OJxEcs0w_kE
// 2: https://www.youtube.com/watch?v=QQx_NmCIuCY

// For more:
// https://github.com/CodingTrain/QuadTree
"""

from pycreative.app import Sketch
from QuadTree import Point, Rectangle, QuadTree


class Example_5_13_QuadTree(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 5.13 QuadTree")
        boundary = Rectangle(self.width / 2, self.height / 2, self.width, self.height)
        self.qtree = QuadTree(self, boundary, 8)
        import random
        for _ in range(2000):
            mean = self.width / 2.0
            stdDev = self.width / 8.0
            x = random.gauss(mean, stdDev)
            y = random.gauss(mean, stdDev)
            p = Point(x, y)
            self.qtree.insert(p)

    def draw(self):
        self.clear((255, 255, 255))
        self.qtree.show()

        rect_mode = 'CENTER'
        range = Rectangle(self.mouse_x or 0, self.mouse_y or 0, 50, 50)

        # This check has been introduced due to a bug discussed in
        # https://github.com/CodingTrain/website/pull/556
        if (self.mouse_x or 0) < self.width and (self.mouse_y or 0) < self.height:
            self.stroke(255, 50, 50)
            self.stroke_weight(2)
            self.fill(255, 50, 50, 50)
            self.rect_mode(rect_mode)
            self.rect(range.x, range.y, range.w * 2, range.h * 2)
            points = []
            points = self.qtree.query(range, points)
            print(points)
            for p in points:
                self.stroke(50, 50, 50)
                self.stroke_weight(3)
                self.point(p.x, p.y)
