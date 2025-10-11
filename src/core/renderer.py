"""Renderer: dispatch descriptors to adapter draw methods.

This renderer is intentionally tiny: it keeps no drawing logic and simply maps
descriptor types to adapter methods. Adapters implement the real drawing.
"""

from typing import Any, Dict, Iterable


class Renderer:
    def __init__(self, adapter: Any):
        self._adapter = adapter
        # Adapter is expected to provide a small set of drawing methods. The
        # dispatch map is kept minimal here and can be extended by callers.
        self._dispatch = {
            'line': getattr(adapter, 'draw_line', None),
            'rect': getattr(adapter, 'draw_rect', None),
            'circle': getattr(adapter, 'draw_circle', None),
            'polygon': getattr(adapter, 'draw_polygon', None),
        }

    def render(self, descriptors: Iterable[Dict]) -> None:
        for d in descriptors:
            t = d.get('type')
            fn = self._dispatch.get(t)
            if fn is None:
                raise ValueError(f'Unknown descriptor type "{t}" or adapter missing method')
            args = d.get('args', {})
            fn(**args)
