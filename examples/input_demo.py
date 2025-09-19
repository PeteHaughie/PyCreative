"""
Example usage of pycreative.input unified event dispatch.
"""
import pygame
from pycreative import Sketch, dispatch_event, Event

class InputSketch(Sketch):
    def setup(self):
        self.size(400, 300)
        self.bg = (0, 0, 0)
        self.last_event = None
    def on_event(self, event: Event):
        self.last_event = event
        print(f"Event: {event}")
    def draw(self):
        self.clear(self.bg)
        # Optionally draw something based on last_event

if __name__ == "__main__":
    pygame.init()
    sketch = InputSketch()
    screen = pygame.display.set_mode((sketch.width, sketch.height))
    sketch._screen = screen
    sketch.setup()
    running = True
    while running:
        for event in pygame.event.get():
            dispatch_event(sketch, event)
            if event.type == pygame.QUIT:
                running = False
        sketch.draw()
        pygame.display.flip()
    pygame.quit()
