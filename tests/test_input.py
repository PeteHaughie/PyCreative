"""
Unit tests for pycreative.input.Event normalization and dispatch.
"""

from pycreative import Event, dispatch_event



from pycreative import Sketch

class SketchForTest(Sketch):
    def __init__(self):
        super().__init__()
        self.events = []

    def on_event(self, event):
        self.events.append(event)


def test_key_event():
    class DummyPygameEvent:
        type = 768  # KEYDOWN
        key = 32

    e = Event.from_pygame(DummyPygameEvent())
    assert e.type == "key" and e.key == 32


def test_mouse_event():
    class DummyPygameEvent:
        type = 1025  # MOUSEBUTTONDOWN
        pos = (10, 20)
        button = 1

    e = Event.from_pygame(DummyPygameEvent())
    assert e.type == "mouse" and e.pos == (10, 20) and e.button == 1


def test_dispatch_event():
    class DummyPygameEvent:
        type = 768  # KEYDOWN
        key = 65

    sketch = SketchForTest()
    dispatch_event(sketch, DummyPygameEvent())
    assert sketch.events[0].type == "key" and sketch.events[0].key == 65
