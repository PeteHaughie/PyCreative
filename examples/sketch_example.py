# A minimal example of a PyCreative sketch

"""Self-contained example sketch.

This example defines a minimal Sketch class so it can be run directly in the
development layout without importing a legacy `pycreative.app`. The real
framework provides a richer `Sketch` in the installed package; this example
is intentionally tiny and demonstrates the CLI contract (a module-level
`Sketch` class with `setup` and `draw`).
"""

class Sketch:
    def __init__(self):
        self.width = 800
        self.height = 600

    def setup(self):
        # Sketches are expected to call size() in setup; record values here
        self.size(800, 600)

    def size(self, w, h, fullscreen=False):
        self.width = w
        self.height = h

    def draw(self):
        # This minimal example doesn't perform real drawing; it demonstrates
        # the expected API shape so the CLI and engine can exercise lifecycle.
        pass
