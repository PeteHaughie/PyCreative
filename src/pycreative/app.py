from __future__ import annotations

from typing import Optional, Tuple

import time
import pygame

from . import input as input_mod


class Sketch:
    """Minimal Sketch runtime: lifecycle hooks and a pygame-based run loop.

    This is intentionally small and focused on the lifecycle and basic drawing helpers
    so examples and tests can run during bootstrapping.
    """

    def __init__(self, sketch_path: Optional[str] = None) -> None:
        # Optional path to the user sketch file that instantiated this Sketch
        self.sketch_path: Optional[str] = sketch_path
        self.width: int = 640
        self.height: int = 480
        self.fullscreen: bool = False
        self._frame_rate: int = 60
        self._surface: Optional[pygame.Surface] = None
        self._clock: Optional[pygame.time.Clock] = None
        self._running: bool = False
        self.frame_count: int = 0
        self._title: str = "PyCreative"

    # --- Lifecycle hooks (override in subclasses) ---
    def setup(self) -> None:
        return None

    def update(self, dt: float) -> None:
        return None

    def draw(self) -> None:
        return None

    def on_event(self, event: input_mod.Event) -> None:
        return None

    def teardown(self) -> None:
        return None

    # --- Helpers ---
    def size(self, w: int, h: int, fullscreen: bool = False) -> None:
        self.width = int(w)
        self.height = int(h)
        self.fullscreen = bool(fullscreen)

    def set_title(self, title: str) -> None:
        self._title = str(title)
        if pygame.display.get_init():
            pygame.display.set_caption(self._title)

    def frame_rate(self, fps: int) -> None:
        self._frame_rate = int(fps)

    # --- Basic drawing primitives ---
    def clear(self, color: Tuple[int, int, int]) -> None:
        if self._surface is not None:
            self._surface.fill(color)

    def ellipse(self, x: float, y: float, w: float, h: float, fill: Optional[Tuple[int, int, int]] = None, stroke=None) -> None:
        if self._surface is None:
            return
        rect = pygame.Rect(int(x - w / 2), int(y - h / 2), int(w), int(h))
        if fill is not None:
            pygame.draw.ellipse(self._surface, fill, rect)

    # --- Run loop ---
    def run(self, max_frames: Optional[int] = None) -> None:
        pygame.init()
        # Call setup early so user can call self.size() there
        try:
            self.setup()
        except Exception:
            # setup exceptions should not crash import; re-raise
            raise

        flags = 0
        if self.fullscreen:
            flags = pygame.FULLSCREEN

        self._surface = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption(self._title)
        self._clock = pygame.time.Clock()
        self._running = True

        last_time = time.perf_counter()
        while self._running:
            now = time.perf_counter()
            dt = now - last_time
            last_time = now

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._running = False
                else:
                    input_mod.dispatch_event(self, ev)

            try:
                self.update(dt)
                self.draw()
            except Exception:
                # On error, attempt teardown and stop
                try:
                    self.teardown()
                finally:
                    self._running = False
                    raise

            pygame.display.flip()
            self.frame_count += 1
            # If max_frames is provided, stop after reaching it
            if max_frames is not None and self.frame_count >= int(max_frames):
                self._running = False
            # enforce framerate
            if self._clock is not None:
                self._clock.tick(self._frame_rate)

        # Clean up
        try:
            self.teardown()
        finally:
            pygame.quit()
