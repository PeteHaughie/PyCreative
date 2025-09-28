"""
input_demo.py: Example sketch showing event handling in Sketch format.
"""

from pycreative import Sketch


class InputDemo(Sketch):
    def setup(self):
        self.size(400, 300)
        self.bg = (0, 0, 0)
        self.last_event = None

    def on_event(self, event):
        self.last_event = event
        print(f"Event: {event}")

    # Event helpers for discoverability
    def event_type(self):
        if self.last_event is not None:
            return getattr(self.last_event, "type", None)
        return None

    def event_key(self):
        if self.last_event is not None and hasattr(self.last_event, "key"):
            return self.last_event.key
        return None

    def event_mouse_pos(self):
        if self.last_event is not None and hasattr(self.last_event, "pos"):
            return self.last_event.pos
        return None

    def draw(self):
        self.clear(self.bg)
        # Optionally draw something based on last_event

    def teardown(self):
        # Clean up resources if needed (no-op for the example)
        pass


if __name__ == "__main__":
    InputDemo().run()
