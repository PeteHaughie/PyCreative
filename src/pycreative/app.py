"""
pycreative.app: Main Sketch class and app loop for PyCreative.
"""
import pygame

from pycreative.graphics import Surface

from dataclasses import dataclass

import time

from typing import Any, Optional


@dataclass
class Pos:
    x: int = 0
    y: int = 0

class Mouse:
    def reset(self):
        self.left_up = False
        self.middle_up = False
        self.right_up = False
        self.left_down = False
        self.middle_down = False
        self.right_down = False
    def __init__(self):
        self.pos = Pos()
        self.scroll = 0
        self.left = False
        self.middle = False
        self.right = False
        self.left_up = False
        self.middle_up = False
        self.right_up = False
        self.left_down = False
        self.middle_down = False
        self.right_down = False

class Sketch:
    def radians(self, degrees: float) -> float:
        """
        Convert degrees to radians using pycreative.math.radians.
        Usage:
            angle_rad = self.radians(90)
        """
        from pycreative.math import radians
        return radians(degrees)

    def image(
        self,
        img,
        x: float,
        y: float,
        w: "Optional[float]" = None,
        h: "Optional[float]" = None,
    ):
        """
        Draw an image (pygame.Surface) at (x, y). If w and h are provided, scale the image.
        """
        if self._surface:
            self._surface.image(img, x, y, w, h)

    def load_image(self, path: str):
        """
        Load an image using the Assets manager.
        Usage:
            img = self.load_image("image.png")
        """
        return self.assets.load_image(path)

    """
    Base class for PyCreative sketches. Implements lifecycle hooks and main loop.

    Usage example:
    >>> class MySketch(Sketch):
    ...     def setup(self):
    ...         self.size(800, 600)
    ...         self.set_title("My Sketch")
    ...         self.bg = 0
    ...     def draw(self):
    ...         self.clear(0)
    ...         self.ellipse(self.width//2, self.height//2, 200, 200)
    ...
    >>> MySketch().run()
    """

    def __init__(self, sketch_path: Optional[str] = None):
        import inspect
        import os
        import sys
        self.mouse = Mouse()
        self.width = 640
        self.height = 480
        self.fullscreen = False
        self.bg = 0
        self._screen: Optional[pygame.Surface] = None
        self._surface: Optional[Surface] = None
        self._clock: Optional[pygame.time.Clock] = None
        self._running = False
        self._frame_rate = 60
        self.t = 0.0
        self.frame_count = 0
        # Store sketch directory for asset loading
        sketch_dir = None
        if sketch_path and os.path.exists(sketch_path):
            sketch_dir = os.path.dirname(os.path.abspath(sketch_path))
        else:
            # Fallback: previous logic
            script_path = sys.argv[0]
            if script_path.endswith(".py") and os.path.exists(script_path):
                sketch_dir = os.path.dirname(os.path.abspath(script_path))
            else:
                venv_paths = [".venv", "env", "bin", "Scripts"]
                frame = inspect.currentframe()
                while frame:
                    filename = frame.f_globals.get("__file__", None)
                    if filename and filename.endswith(".py"):
                        abs_path = os.path.abspath(filename)
                        if "pycreative" not in abs_path and not any(
                            p in abs_path for p in venv_paths
                        ):
                            sketch_dir = os.path.dirname(abs_path)
                            break
                    frame = frame.f_back
                if not sketch_dir:
                    main_file = getattr(sys.modules.get("__main__"), "__file__", None)
                    if main_file and main_file.endswith(".py"):
                        sketch_dir = os.path.dirname(os.path.abspath(main_file))
                    else:
                        sketch_dir = os.getcwd()
        self._sketch_dir = sketch_dir
        # Asset manager
        from pycreative.assets import Assets

        self.assets = Assets(self._sketch_dir)
        # Math utilities
        import pycreative.math as _math

        self.math = _math

    def size(self, width: int, height: int, fullscreen: bool = False):
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

    def frame_rate(self, fps: int):
        self._frame_rate = fps

    def clear(self, color: Any = 0):
        if self._surface:
            self._surface.surface.fill(color)

    def ellipse(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        color: Any = (255, 255, 255),
        width: int = 0,
    ):
        """
        Draw an ellipse centered at (x, y) with width w and height h.
        Parameters:
        - x, y: Center coordinates
        - w, h: Width and height
        - color: RGB tuple
        - width: Border thickness (0 = filled)
        """
        if self._surface:
            self._surface.ellipse(x, y, w, h, color, width)

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        color: Any = (255, 255, 255),
        width: int = 0,
    ):
        if self._surface:
            self._surface.rect(x, y, w, h, color, width)

    def line(
        self, start: tuple, end: tuple, color: Any = (255, 255, 255), width: int = 1
    ):
        """
        Draw a line between two points.

        Parameters:
        - start: (x, y) tuple for start point
        - end: (x, y) tuple for end point
        - color: RGB tuple
        - width: Line thickness
        """
        if self._surface:
            self._surface.line(start, end, color, width)
    
    def triangle(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        color: Any = (255, 255, 255),
        width: int = 0,
    ):
        if self._surface:
            self._surface.triangle(x1, y1, x2, y2, x3, y3, color, width)
    
    def quad(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        x4: float,
        y4: float,
        color: Any = (255, 255, 255),
        width: int = 0,
    ):
        if self._surface:
            self._surface.quad(x1, y1, x2, y2, x3, y3, x4, y4, color, width)

    def arc(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        start_angle: float,
        end_angle: float,
        color: Any = (255, 255, 255),
        width: int = 1,
        mode: str = "open",  # "open", "chord", or "pie"
    ):
        if self._surface:
            self._surface.arc(x, y, w, h, start_angle, end_angle, color, width, mode)

    def bezier(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        x4: float,
        y4: float,
        color: Any = (255, 255, 255),
        width: int = 1,
        segments: int = 20,
    ):
        """
        Draw a cubic Bezier curve from (x1, y1) to (x4, y4) with control points (x2, y2), (x3, y3).
        """
        if self._surface:
            self._surface.bezier(
                x1, y1, x2, y2, x3, y3, x4, y4, color, width, segments
            )

    def set_title(self, title: str):
        self._custom_title = title
        pygame.display.set_caption(title)

    def run(self, max_frames: Optional[int] = None):
        pygame.init()
        self._running = True
        self.setup()
        # Set window title after setup so user can override it
        self.set_title(getattr(self, "_custom_title", type(self).__name__))
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self._screen = pygame.display.set_mode((self.width, self.height), flags)
        self._surface = Surface(self._screen)
        self._clock = pygame.time.Clock()
        start_time = time.time()
        while self._running:
            self.mouse.reset()  # <-- Move reset to start of frame
            dt = self._clock.tick(self._frame_rate) / 1000.0
            self.t = time.time() - start_time
            self.update(dt)
            events = list(pygame.event.get())
            if not events:
                pygame.event.pump()
            from pycreative.input import dispatch_event
            for event in events:
                dispatch_event(self, event)
                if event.type == pygame.QUIT:
                    self._running = False
            self.frame_count += 1
            if max_frames is not None and self.frame_count > max_frames:
                print(f"[Sketch.run] Reached max_frames: {max_frames}, closing sketch.")
                self._running = False
                continue
            self.draw()
            pygame.display.flip()
        self.shutdown()

    def setup(self):
        """
        Override this method to add setup code for your sketch.
        """
        pass

    def update(self, dt: float):
        """
        Override this method to add update logic for your sketch.

        Parameters:
        - dt: Time in seconds since the last frame.
        """
        pass

    def draw(self):
        """
        Override this method to add drawing code for your sketch.
        """
        pass

    def on_event(self, event):
        # Update mouse object for idiomatic access
        if hasattr(event, "type") and event.type in ("mouse", "motion"):
            if hasattr(event, "pos") and event.pos:
                self.mouse.pos.x = event.pos[0]
                self.mouse.pos.y = event.pos[1]
            # Do not reset button states on mouse motion; only update on button events
            if hasattr(event, "button"):
                # Button: 1=left, 2=middle, 3=right
                btn = event.button
                if hasattr(event, "raw"):
                    raw_type = getattr(event.raw, "type", None)
                    import pygame
                    if raw_type == pygame.MOUSEBUTTONDOWN:
                        if btn == 1:
                            self.mouse.left = True
                            self.mouse.left_down = True
                            print(f"Mouse left button DOWN at {getattr(event, 'pos', None)}")
                        elif btn == 2:
                            self.mouse.middle = True
                            self.mouse.middle_down = True
                        elif btn == 3:
                            self.mouse.right = True
                            self.mouse.right_down = True
                    elif raw_type == pygame.MOUSEBUTTONUP:
                        if btn == 1:
                            self.mouse.left = False
                            self.mouse.left_up = True
                            print(f"Mouse left button UP at {getattr(event, 'pos', None)}")
                        elif btn == 2:
                            self.mouse.middle = False
                            self.mouse.middle_up = True
                        elif btn == 3:
                            self.mouse.right = False
                            self.mouse.right_up = True
            # TODO: Add scroll wheel support if available in event

    def shutdown(self):
        """
        Override this method to add cleanup code for your sketch.
        """
        pass
