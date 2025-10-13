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
            'square': getattr(adapter, 'draw_rect', None),
            'circle': getattr(adapter, 'draw_circle', None),
            'polygon': getattr(adapter, 'draw_polygon', None),
            'background': getattr(adapter, 'draw_background', None),
        }

    def render(self, descriptors: Iterable[Dict]) -> None:
        for d in descriptors:
            t = d.get('type')
            args = d.get('args', {})

            # Special-case: square maps to draw_rect with width/height = s
            if t == 'square':
                # convert args {x,y,s,..} -> draw_rect(x,y,w=s,h=s,...)
                x = args.get('x')
                y = args.get('y')
                s = args.get('s')
                # Preserve fill/stroke semantics
                fill = args.get('fill')
                stroke = args.get('stroke')
                stroke_weight = args.get('stroke_weight', 0)
                fn = getattr(self._adapter, 'draw_rect', None)
                if fn is None:
                    raise ValueError('Adapter missing draw_rect required for square')
                # Call draw_rect with converted args
                try:
                    fn(x, y, s, s, color=fill, stroke=stroke, stroke_weight=stroke_weight)
                except Exception:
                    pass
                continue

            fn = self._dispatch.get(t)
            if fn is None:
                try:
                    from src.core.debug import debug
                    debug(f"Renderer: unknown descriptor type '{t}' (adapter missing method)")
                except Exception:
                    pass
                continue

            # Emit a debug trace for dispatched descriptors when debug mode enabled
            try:
                from src.core.debug import debug
                debug(f"Renderer: dispatching type={t} args={args}")
            except Exception:
                pass

            try:
                # Special-case background for observability
                if t == 'background':
                    from src.core.debug import debug
                    debug(f"Renderer: dispatching background with args={args}")
            except Exception:
                pass

            try:
                # Debug: log the adapter instance and its engine/display surface
                try:
                    from src.core.debug import debug
                    adapter_inst = getattr(fn, '__self__', None)
                    eng_obj = getattr(adapter_inst, '_engine', None)
                    disp = getattr(eng_obj, '_display_surface', None)
                    debug(f"Renderer: calling fn={getattr(fn,'__name__',repr(fn))} adapter={adapter_inst} engine={eng_obj} display_surface={type(disp) if disp is not None else None}")
                except Exception:
                    pass
                fn(**args)
            except Exception:
                pass
