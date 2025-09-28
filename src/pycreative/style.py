"""
pycreative.style: Shared style state and API for Sketch and GraphicsSurface.

Provides fill, stroke, noFill, noStroke, stroke_weight methods and state.
"""
from typing import Any, Optional

class GraphicsStyle:
    _rect_mode: str = "corner"

    def rect_mode(self, mode: str):
        """
        Set the rectangle drawing mode.
        Modes:
            'corner'  (default): x, y is top-left, w/h are width/height
            'center': x, y is center, w/h are width/height
            'corners': x, y and w, h are opposite corners
        Usage:
            self.rect_mode('center')
        """
        if mode not in ("corner", "center", "corners"):
            raise ValueError(f"rect_mode must be 'corner', 'center', or 'corners', got '{mode}'")
        self._rect_mode = mode
    _fill: Optional[Any] = (255, 255, 255)
    _do_fill: bool = True
    _stroke: Optional[Any] = (0, 0, 0)
    _do_stroke: bool = True
    _stroke_weight: int = 1

    def fill(self, *args):
        """Set fill color."""
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
        """Set stroke color."""
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
        """Set stroke width."""
        self._stroke_weight = w

    def get_style(self):
        """Return current style state as a dict."""
        return dict(
            fill=self._fill if self._do_fill else None,
            stroke=self._stroke if self._do_stroke else None,
            stroke_weight=self._stroke_weight if self._do_stroke else 0,
        )
