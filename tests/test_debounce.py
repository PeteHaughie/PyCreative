import pytest
from pycreative.app import Sketch, Mouse
import pygame

class DebounceSketch(Sketch):
    def __init__(self):
        super().__init__()
        self.size(100, 100)
        self.events = []
        self._screen = pygame.Surface((self.width, self.height))
        from pycreative.graphics import Surface
        self._surface = Surface(self._screen)
        self._frame_rate = 60
        self._clock = pygame.time.Clock()
        self._running = False
        self.mouse = Mouse()
        self._mouse_event_queue = []

    def draw(self):
        # Process mouse event queue before checking flags
        self._process_mouse_event_queue()
        if self.mouse.left_down:
            self.events.append('left_down')
        if self.mouse.left_click:
            self.events.append('left_click')


def test_mouse_debounce():
    sketch = DebounceSketch()
    # Frame 1: Simulate mouse down event
    sketch.mouse.reset()
    sketch._mouse_event_queue.append((pygame.MOUSEBUTTONDOWN, 1, (50, 50)))
    sketch.draw()
    # Frame 2: No event, left_down should be False
    sketch.mouse.reset()
    sketch.draw()
    # Frame 3: Simulate mouse up event
    sketch.mouse.reset()
    sketch._mouse_event_queue.append((pygame.MOUSEBUTTONUP, 1, (50, 50)))
    sketch.draw()
    # Frame 4: No event, left_click should be False
    sketch.mouse.reset()
    sketch.draw()
    # Check debounce: left_down only on frame 1, left_click only on frame 3
    assert sketch.events == ['left_down', 'left_click'], f"Expected ['left_down', 'left_click'], got {sketch.events}"
