"""
Confetti class for Example 4.5: Particle System with Inheritance and Polymorphism
"""

from Particle import Particle


class Confetti(Particle):
  def __init__(self, sketch, x=0.0, y=0.0):
    super().__init__(sketch, x, y)

  def show(self):
    angle = self.sketch.map(self.position.x, 0, self.sketch.width, 0, self.sketch.TWO_PI)
    self.sketch.rect_mode("CENTER")
    self.sketch.fill(self.lifespan)
    self.sketch.stroke(self.lifespan)
    self.sketch.stroke_weight(2)
    self.sketch.push_matrix()
    self.sketch.translate(self.position.x, self.position.y)
    self.sketch.rotate(angle)
    self.sketch.rect(0, 0, 12, 12)
    self.sketch.pop_matrix()
