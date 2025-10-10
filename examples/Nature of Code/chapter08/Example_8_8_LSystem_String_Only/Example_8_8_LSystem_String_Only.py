"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter8/Example_8_8_LSystem_String_Only/Example_8_8_LSystem_String_Only.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Simple L-system Sentence Generation
"""

from pycreative.app import Sketch


class Example_8_8_LSystem_String_Only(Sketch):
  def setup(self):
    self.size(640, 160)

    # (optional) list_fonts() is available to explore bundled/system fonts

    # Try to set a monospace font succinctly: prefer TTF/OTF system fonts
    # (use_font will prefer non-.ttc matches like 'Courier New') and fall
    # back to the default if none are available.
    for candidate in ('courier new', 'courier', 'monospace'):
      if self.use_font(candidate, size=16):
        break

    self.set_title("Example 8-8: L-System String Only")
    self.text_size(14)
    self.fill(0)
    self.current = "A"
    self.no_loop()

  def draw(self):
    self.background(255)

    self.push_matrix()
    try:
      self.translate(0, -16)
      for i in range(9):
        self.generate()
        # Draw using the active font (the Sketch convenience API
        # ensures a reasonable default when requested in setup()).
        self.text(f"{i}: {self.current}", 4, 20 + i * 16)
    finally:
      self.pop_matrix()

  def generate(self):
    next_s = ""
    for c in self.current:
      if c == 'A':
        next_s += "AB"
      elif c == 'B':
        next_s += "A"
    self.current = next_s