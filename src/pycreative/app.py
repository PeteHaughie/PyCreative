"""
pycreative.app: Main Sketch class and app loop for PyCreative.
"""

import pygame


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
        self.left_click = False
        self.middle_click = False
        self.right_click = False

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
        self.left_click = False
        self.middle_click = False
        self.right_click = False
        self._down_this_frame = {1: False, 2: False, 3: False}
        self._clicked_this_frame = {1: False, 2: False, 3: False}


class Sketch:
    def polyline(self, points, color=(255, 255, 255), width: int = 1):
        """
        Draw a multi-segmented straight line through the given points.
        """
        if self._surface:
            self._surface.polyline(points, color=color, width=width)
    def text(self, s, x, y, center=False, color=(0,0,0), size=20):
        """
        Draw text at (x, y) with optional centering, color, and size.
        Uses Cairo-native text rendering in Cairo mode.
        """
        if hasattr(self, '_surface') and self._surface:
            # Use Cairo-native text if available
            if hasattr(self._surface, 'text'):
                self._surface.text(s, x, y, color=color, size=size, center=center)
                return
        # Fallback to PyGame
        import pygame
        if not hasattr(self, '_screen') or self._screen is None:
            return
        font = pygame.font.SysFont(None, size)
        surf = font.render(s, True, color)
        rect = surf.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self._screen.blit(surf, rect)

    def video(self, player, x: int, y: int, w: int, h: int):
        """
        Draw a video frame from a MediaPlayer at (x, y) with width w and height h.
        """
        if player and hasattr(player, 'resize') and self._screen:
            frame = player.resize(w, h)
            if frame:
                self._screen.blit(frame, (x, y))
    # --- Global style state ---
    _fill: Optional[Any] = (255, 255, 255)
    _do_fill: bool = True
    _stroke: Optional[Any] = (0, 0, 0)
    _do_stroke: bool = True
    _stroke_weight: int = 1

    def fill(self, *args):
        """Set global fill color."""
        if len(args) == 0:
            self._fill = None
        elif len(args) > 1:
            self._fill = args
        else:
            self._fill = args[0]
        self._do_fill = True

    def noFill(self):
        """Disable fill for subsequent shapes."""
        self._do_fill = False
    def stroke(self, *args):
        """Set global stroke color."""
        if len(args) == 0:
            self._stroke = None
        elif len(args) > 1:
            self._stroke = args
        else:
            self._stroke = args[0]
        self._do_stroke = True

    def noStroke(self):
        """Disable stroke for subsequent shapes."""
        self._do_stroke = False

    def stroke_weight(self, w: int):
        """Set global stroke width."""
        self._stroke_weight = w

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
        self._mouse_event_queue = []
        self.width = 640
        self.height = 480
        self.fullscreen = False
        self.bg = 0
        self._screen: Optional[pygame.Surface] = None
        # Accept both Surface and CairoSurface
        self._surface: Optional[Any] = None
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
        # Print available UVC devices on Sketch init
        try:
            from pycreative.capture import list_devices
            list_devices()
        except Exception as e:
            print(f"[Sketch] Could not list UVC devices: {e}")

    def size(
        self, width: int, height: int, fullscreen: bool = False, mode: str = "cairo"
    ):
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self._backend_mode = mode

    def frame_rate(self, fps: int):
        self._frame_rate = fps

    def clear(self, color: Any = 0):
        if self._surface:
            # CairoSurface backend
            from pycreative.graphics import CairoSurface

            if isinstance(self._surface, CairoSurface):
                self._surface.clear(color)
            else:
                self._surface.surface.fill(color)

    def on_event(self, event):
        # Update mouse object for idiomatic access
        if hasattr(event, "type") and event.type in ("mouse", "motion"):
            if hasattr(event, "pos") and event.pos:
                self.mouse.pos.x = event.pos[0]
                self.mouse.pos.y = event.pos[1]
            # Queue mouse button events for processing after draw
            if hasattr(event, "button"):
                btn = event.button
                if hasattr(event, "raw"):
                    raw_type = getattr(event.raw, "type", None)
                    import pygame
                    if raw_type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                        self._mouse_event_queue.append((raw_type, btn, event.pos))
                        print(f"[MouseQueue] Queued event: {raw_type}, btn={btn}, pos={event.pos}")
            # TODO: Add scroll wheel support if available in event

    def ellipse(
            self,
            x: float,
            y: float,
            w: float,
            h: float,
            fill: Any = None,
            stroke: Any = None,
            stroke_width: Optional[int] = None,
        ):
            """
            Draw an ellipse centered at (x, y) with width w and height h.
            Per-call fill/stroke/stroke_width override global state.
            """
            use_fill = fill if fill is not None else (self._fill if self._do_fill else None)
            use_stroke = (
                stroke
                if stroke is not None
                else (self._stroke if self._do_stroke else None)
            )
            use_stroke_width = (
                stroke_width
                if stroke_width is not None
                else (self._stroke_weight if self._do_stroke else 0)
            )
            # Draw fill (if enabled)
            if self._surface and use_fill is not None:
                self._surface.ellipse(x, y, w, h, use_fill, 0)
            # Draw stroke (if enabled)
            if self._surface and use_stroke is not None and use_stroke_width > 0:
                self._surface.ellipse(x, y, w, h, use_stroke, use_stroke_width)

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: Any = None,
        stroke: Any = None,
        stroke_width: Optional[int] = None,
    ):
        """
        Draw a rectangle at (x, y) with width w and height h.
        Per-call fill/stroke/stroke_width override global state.
        """
        use_fill = fill if fill is not None else (self._fill if self._do_fill else None)
        use_stroke = (
            stroke
            if stroke is not None
            else (self._stroke if self._do_stroke else None)
        )
        use_stroke_width = (
            stroke_width
            if stroke_width is not None
            else (self._stroke_weight if self._do_stroke else 0)
        )
        # Draw fill (if enabled)
        if self._surface and use_fill is not None:
            self._surface.rect(x, y, w, h, use_fill, 0)
        # Draw stroke (if enabled)
        if self._surface and use_stroke is not None and use_stroke_width > 0:
            self._surface.rect(x, y, w, h, use_stroke, use_stroke_width)

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        stroke: Any = None,
        stroke_width: Optional[int] = None,
    ):
        """
        Draw a line from (x1, y1) to (x2, y2).
        Per-call stroke/stroke_width override global state.
        """
        use_stroke = (
            stroke
            if stroke is not None
            else (self._stroke if self._do_stroke else None)
        )
        use_stroke_width = (
            stroke_width
            if stroke_width is not None
            else (self._stroke_weight if self._do_stroke else 0)
        )
        if self._surface and use_stroke is not None and use_stroke_width > 0:
            self._surface.line(x1, y1, x2, y2, use_stroke, use_stroke_width)

    def triangle(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        fill: Any = None,
        stroke: Any = None,
        stroke_width: Optional[int] = None,
    ):
        use_fill = fill if fill is not None else (self._fill if self._do_fill else None)
        use_stroke = (
            stroke
            if stroke is not None
            else (self._stroke if self._do_stroke else None)
        )
        use_stroke_width = (
            stroke_width
            if stroke_width is not None
            else (self._stroke_weight if self._do_stroke else 0)
        )
        # Draw fill
        if self._surface and use_fill is not None:
            self._surface.triangle(x1, y1, x2, y2, x3, y3, use_fill, 0)
        # Draw stroke
        if self._surface and use_stroke is not None and use_stroke_width > 0:
            self._surface.triangle(x1, y1, x2, y2, x3, y3, use_stroke, use_stroke_width)

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
        fill: Any = None,
        stroke: Any = None,
        stroke_width: Optional[int] = None,
    ):
        use_fill = fill if fill is not None else (self._fill if self._do_fill else None)
        use_stroke = (
            stroke
            if stroke is not None
            else (self._stroke if self._do_stroke else None)
        )
        use_stroke_width = (
            stroke_width
            if stroke_width is not None
            else (self._stroke_weight if self._do_stroke else 0)
        )
        # Draw fill
        if self._surface and use_fill is not None:
            self._surface.quad(x1, y1, x2, y2, x3, y3, x4, y4, use_fill, 0)
        # Draw stroke
        if self._surface and use_stroke is not None and use_stroke_width > 0:
            self._surface.quad(
                x1, y1, x2, y2, x3, y3, x4, y4, use_stroke, use_stroke_width
            )

    def arc(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        start_angle: float,
        end_angle: float,
        fill: Any = None,
        stroke: Any = None,
        stroke_width: Optional[int] = None,
        mode: str = "open",
    ):
        use_fill = fill if fill is not None else (self._fill if self._do_fill else None)
        use_stroke = (
            stroke
            if stroke is not None
            else (self._stroke if self._do_stroke else None)
        )
        use_stroke_width = (
            stroke_width
            if stroke_width is not None
            else (self._stroke_weight if self._do_stroke else 0)
        )
        # Draw fill arc (if enabled)
        if self._surface and use_fill is not None:
            self._surface.arc(x, y, w, h, start_angle, end_angle, use_fill, 0, mode)
        # Draw stroke arc (if enabled)
        if self._surface and use_stroke is not None and use_stroke_width > 0:
            self._surface.arc(
                x, y, w, h, start_angle, end_angle, use_stroke, use_stroke_width, mode
            )

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
        fill: Any = None,
        stroke: Any = None,
        stroke_width: Optional[int] = None,
        segments: int = 20,
    ):
        use_fill = fill if fill is not None else (self._fill if self._do_fill else None)
        use_stroke = (
            stroke
            if stroke is not None
            else (self._stroke if self._do_stroke else None)
        )
        use_stroke_width = (
            stroke_width
            if stroke_width is not None
            else (self._stroke_weight if self._do_stroke else 0)
        )
        # Draw fill (if enabled)
        if self._surface and use_fill is not None:
            self._surface.bezier(x1, y1, x2, y2, x3, y3, x4, y4, use_fill, 0, segments)
        # Draw stroke (if enabled)
        if self._surface and use_stroke is not None and use_stroke_width > 0:
            self._surface.bezier(
                x1, y1, x2, y2, x3, y3, x4, y4, use_stroke, use_stroke_width, segments
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
        # Backend selection
        if hasattr(self, "_backend_mode") and self._backend_mode == "cairo":
            from pycreative.graphics import CairoSurface

            self._surface = CairoSurface(self.width, self.height)
        else:
            from pycreative.graphics import Surface

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
            # Call user's draw method if overridden
            user_draw = getattr(type(self), "draw", None)
            if user_draw is not None and user_draw is not Sketch.draw:
                user_draw(self)
            # Call backend display logic
            Sketch.draw(self)
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
        Handles backend display for PyGame and Cairo automatically.
        Users should not call super().draw().
        """
        from pycreative.graphics import CairoSurface

        # Process mouse event queue before user draw
        self._process_mouse_event_queue()

        display_surface = pygame.display.get_surface()
        if display_surface is None:
            print(
                f"[Sketch.draw] display_surface is None! (frame {getattr(self, 'frame_count', None)})"
            )
            return
        if (
            hasattr(self, "_backend_mode")
            and self._backend_mode == "cairo"
            and isinstance(self._surface, CairoSurface)
        ):
            try:
                pg_surface = self._surface.to_pygame_surface()
                display_surface.blit(pg_surface, (0, 0))
                pygame.display.update()
            except Exception as e:
                print(f"[Sketch.draw] Exception during CairoSurface blit: {e}")
        # --- User draw logic ---
        user_draw = getattr(type(self), "draw", None)
        if user_draw is not None and user_draw is not Sketch.draw:
            # Call user's draw method, but avoid recursion
            user_draw(self)

    def _process_mouse_event_queue(self):
        # Only set one-shot flags once per frame, based on final event state
        for raw_type, btn, pos in self._mouse_event_queue:
            import pygame
            if raw_type == pygame.MOUSEBUTTONDOWN:
                if btn == 1:
                    self.mouse.left = True
                    self.mouse.left_down = True
                    print(f"[MouseQueue] Processed DOWN: btn={btn}, pos={pos}")
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
                    self.mouse.left_click = True
                    print(f"[MouseQueue] Processed UP: btn={btn}, pos={pos}")
                elif btn == 2:
                    self.mouse.middle = False
                    self.mouse.middle_up = True
                    self.mouse.middle_click = True
                elif btn == 3:
                    self.mouse.right = False
                    self.mouse.right_up = True
                    self.mouse.right_click = True
        self._mouse_event_queue.clear()

    def shutdown(self):
        """
        Override this method to add cleanup code for your sketch.
        """
        pass
