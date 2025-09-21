"""
input_demo.py: Example sketch showing event handling in Sketch format.
"""

from pycreative import Sketch, Event


class InputDemo(Sketch):
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
    InputDemo().run()
