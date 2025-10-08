from __future__ import annotations

from typing import List, Tuple, Optional
from ..graphics import Surface


class PShape:
    """Simple vector shape container.

    Stores subpaths as lists of (x, y) coordinates. Style attributes are
    intentionally minimal and mirror the previous monolithic implementation.
    """

    def __init__(self) -> None:
        self.subpaths: List[List[Tuple[float, float]]] = []
        self.fill = None
        self.stroke = (0, 0, 0)
        self.stroke_weight = 1
        self._style_enabled: bool = True
        self.view_box: Optional[Tuple[float, float, float, float]] = None

    def add_subpath(self, pts: List[Tuple[float, float]]) -> None:
        if pts:
            self.subpaths.append(pts)

    def enable_style(self) -> None:
        self._style_enabled = True

    def disable_style(self) -> None:
        self._style_enabled = False

    def draw(self, surface: Surface, x: float = 0, y: float = 0, w: Optional[float] = None, h: Optional[float] = None) -> None:
        # Compute source bounds
        if self.view_box is not None:
            min_x, min_y, orig_w, orig_h = self.view_box
            if orig_w == 0:
                orig_w = 1.0
            if orig_h == 0:
                orig_h = 1.0
            max_x = min_x + orig_w
            max_y = min_y + orig_h
        else:
            min_x = float('inf')
            min_y = float('inf')
            max_x = float('-inf')
            max_y = float('-inf')
            for sub in self.subpaths:
                for px, py in sub:
                    if px < min_x:
                        min_x = px
                    if py < min_y:
                        min_y = py
                    if px > max_x:
                        max_x = px
                    if py > max_y:
                        max_y = py

        if min_x == float('inf'):
            return

        orig_w = max_x - min_x if max_x > min_x else 1.0
        orig_h = max_y - min_y if max_y > min_y else 1.0

        scale_x = 1.0
        scale_y = 1.0
        if w is not None:
            try:
                scale_x = float(w) / orig_w
            except Exception:
                scale_x = 1.0
        if h is not None:
            try:
                scale_y = float(h) / orig_h
            except Exception:
                scale_y = 1.0

        if w is not None and h is None:
            scale_y = scale_x
        if h is not None and w is None:
            scale_x = scale_y

        for sub in self.subpaths:
            pts: List[Tuple[float, float]] = []
            for px, py in sub:
                sx = (px - min_x) * scale_x
                sy = (py - min_y) * scale_y
                pts.append((x + sx, y + sy))
            fill = self.fill if self._style_enabled else None
            stroke = self.stroke if self._style_enabled else None
            stroke_weight = self.stroke_weight if self._style_enabled else None
            if len(pts) >= 3 and pts[0] == pts[-1]:
                surface.polygon_with_style(pts, fill=fill, stroke=stroke, stroke_weight=stroke_weight)
            else:
                surface.polyline_with_style(pts, stroke=stroke, stroke_weight=stroke_weight)
