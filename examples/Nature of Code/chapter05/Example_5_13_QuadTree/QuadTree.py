"""
Point, Rectangle, and QuadTree classes for Example 5-13: QuadTree
"""

class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y


class Rectangle:
  def __init__(self, x, y, w, h):
    self.x = x
    self.y = y
    self.w = w
    self.h = h

  def contains(self, point):
    return (
      point.x >= self.x - self.w
      and point.x < self.x + self.w
      and point.y >= self.y - self.h
      and point.y < self.y + self.h
    )

  def intersects(self, range):
    return not (
      range.x - range.w > self.x + self.w
      or range.x + range.w < self.x - self.w
      or range.y - range.h > self.y + self.h
      or range.y + range.h < self.y - self.h
    )


class QuadTree:
  def __init__(self, sketch, boundary, capacity):
    self.sketch = sketch
    self.boundary = boundary  # Rectangle
    self.capacity = capacity  # int
    self.points = []  # list of Points
    self.divided = False  # bool
    self.northeast = None  # QuadTree
    self.northwest = None  # QuadTree
    self.southeast = None  # QuadTree
    self.southwest = None  # QuadTree

  def subdivide(self):
    x = self.boundary.x
    y = self.boundary.y
    w = self.boundary.w
    h = self.boundary.h
    ne = Rectangle(x + w / 2, y - h / 2, w / 2, h / 2)
    self.northeast = QuadTree(self.sketch, ne, self.capacity)
    nw = Rectangle(x - w / 2, y - h / 2, w / 2, h / 2)
    self.northwest = QuadTree(self.sketch, nw, self.capacity)
    se = Rectangle(x + w / 2, y + h / 2, w / 2, h / 2)
    self.southeast = QuadTree(self.sketch, se, self.capacity)
    sw = Rectangle(x - w / 2, y + h / 2, w / 2, h / 2)
    self.southwest = QuadTree(self.sketch, sw, self.capacity)
    self.divided = True

  def insert(self, point):
    if not self.boundary.contains(point):
      return False

    if len(self.points) < self.capacity:
      self.points.append(point)
      return True
    else:
      if not self.divided:
        self.subdivide()

      # children may be None from static analysis perspective; guard calls
      if self.northeast and self.northeast.insert(point):
        return True
      if self.northwest and self.northwest.insert(point):
        return True
      if self.southeast and self.southeast.insert(point):
        return True
      if self.southwest and self.southwest.insert(point):
        return True

    return False

  def query(self, range, found):
    if not self.boundary.intersects(range):
      return found

    for p in self.points:
      if range.contains(p):
        found.append(p)

    if self.divided:
      if self.northwest:
        self.northwest.query(range, found)
      if self.northeast:
        self.northeast.query(range, found)
      if self.southwest:
        self.southwest.query(range, found)
      if self.southeast:
        self.southeast.query(range, found)

    return found

  def show(self):
    self.sketch.stroke(0)
    self.sketch.no_fill()
    self.sketch.stroke_weight(1)
    self.sketch.rect_mode(self.sketch.CENTER)
    self.sketch.rect(
      self.boundary.x, self.boundary.y, self.boundary.w * 2, self.boundary.h * 2
    )

    for p in self.points:
      self.sketch.stroke_weight(1)
      self.sketch.stroke(0)
      self.sketch.point(p.x, p.y)

    if self.divided:
      if self.northeast:
        self.northeast.show()
      if self.northwest:
        self.northwest.show()
      if self.southeast:
        self.southeast.show()
      if self.southwest:
        self.southwest.show()
