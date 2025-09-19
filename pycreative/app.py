"""
pycreative.app: Main Sketch class and app loop for PyCreative.
"""
import pygame
import time
from typing import Optional, Any

class Sketch:
    """
    Base class for PyCreative sketches. Implements lifecycle hooks and main loop.

    Usage example:
    >>> class MySketch(Sketch):
    ...     def setup(self):
    ...         self.size(800, 600)
    ...     def draw(self):
    ...         self.clear(0)
    ...         self.ellipse(self.width//2, self.height//2, 200, 200)
    ...
    >>> MySketch().run()
    """
    def __init__(self):
        self.width = 640
        self.height = 480
        self.fullscreen = False
        self.bg = 0
        self._screen: Optional[pygame.Surface] = None
        self._clock: Optional[pygame.time.Clock] = None
        self._running = False
        self._frame_rate = 60
        self.t = 0.0
        self.frame_count = 0

    def size(self, width: int, height: int, fullscreen: bool = False):
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

    def frame_rate(self, fps: int):
        self._frame_rate = fps

    def clear(self, color: Any = 0):
        if self._screen:
            self._screen.fill(color)

    def ellipse(self, x: float, y: float, w: float, h: float, color: Any = (255,255,255)):
        if self._screen:
            pygame.draw.ellipse(self._screen, color, (x-w/2, y-h/2, w, h))

    def rect(self, x: float, y: float, w: float, h: float, color: Any = (255,255,255)):
        if self._screen:
            pygame.draw.rect(self._screen, color, (x, y, w, h))

    def run(self, max_frames: Optional[int] = None):
        pygame.init()
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self._screen = pygame.display.set_mode((self.width, self.height), flags)
        self._clock = pygame.time.Clock()
        self._running = True
        self.setup()
        start_time = time.time()
        while self._running:
            dt = self._clock.tick(self._frame_rate) / 1000.0
            self.t = time.time() - start_time
            self.frame_count += 1
            self.update(dt)
            for event in pygame.event.get():
                self.on_event(event)
                if event.type == pygame.QUIT:
                    self._running = False
            self.draw()
            pygame.display.flip()
            if max_frames is not None and self.frame_count >= max_frames:
                self._running = False
        self.teardown()
        pygame.quit()

    def setup(self):
        """Called once before the main loop starts."""
        pass

    def update(self, dt: float):
        """Called every frame before draw. dt is seconds since last frame."""
        pass

    def draw(self):
        """Called every frame after update."""
        pass

    def on_event(self, event: Any):
        """Called for each PyGame event."""
        pass

    def teardown(self):
        """Called once after the main loop ends."""
        pass
