"""Prototype: load SVG via librsvg + pycairo and convert to skia.Path objects.

This module is an optional backend for SVG loading. It intentionally keeps
the dependency on GObject Introspection / librsvg optional and raises a
clear RuntimeError when the native pieces are missing.

Usage:
    from pycreative.shape.cairo_loader import load_svg_cairo
    shape = load_svg_cairo('path/to/module_1.svg')
    assert hasattr(shape, 'skia_paths')
"""
from __future__ import annotations

from typing import List, Optional, Any
import os

try:
    import skia
except Exception:
    raise ImportError('skia-python is required by the Cairo->Skia loader')

_HAS_GI = True
try:
    import gi
    gi.require_version('Rsvg', '2.0')
    from gi.repository import Rsvg
except Exception:  # pragma: no cover - environment dependent
    _HAS_GI = False

try:
    import cairo
except Exception:  # pragma: no cover - environment dependent
    cairo = None


def _ensure_env():
    if not _HAS_GI or cairo is None:
        raise RuntimeError(
            'Cairo-backed SVG loader requires librsvg + pycairo (GObject Introspection). '
            'On macOS: brew install pkg-config cairo librsvg gobject-introspection && '
            'python -m pip install pycairo pygobject'
        )


def load_svg_cairo(path: str) -> Any:
    """Load an SVG using librsvg+pycairo and return a PCShape-like object
    with `skia_paths` containing converted skia.Path objects.
    """
    _ensure_env()

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    # Create an Rsvg handle from file. API differs across Rsvg versions so
    # try common variants.
    handle = None
    try:
        # Newer introspected API: Rsvg.Handle.new_from_file
        if hasattr(Rsvg, 'Handle') and hasattr(Rsvg.Handle, 'new_from_file'):
            handle = Rsvg.Handle.new_from_file(path)
        elif hasattr(Rsvg, 'Handle') and hasattr(Rsvg.Handle, 'new_from_stream'):
            # Fallback: open file and create a GI InputStream? Simpler: use old API below
            pass
    except Exception:
        handle = None

    if handle is None:
        try:
            # older API: Rsvg.Handle() constructor (pygobject-exposed)
            handle = Rsvg.Handle.new_from_file(path)
        except Exception as e:
            # Last attempt: try the procedural API where Rsvg.Handle() may be callable
            try:
                handle = Rsvg.Handle(path)
            except Exception:
                raise RuntimeError(f'failed to construct Rsvg.Handle for {path}: {e}') from e

    # Render into a recording surface so we can extract the drawing path
    try:
        rec = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
        ctx = cairo.Context(rec)
        # Render the SVG onto the cairo context. Rsvg's render API varies.
        if hasattr(handle, 'render_cairo'):
            handle.render_cairo(ctx)
        elif hasattr(handle, 'render'):
            # older names
            handle.render(ctx)
        else:
            raise RuntimeError('Rsvg handle has no render method')
    except Exception as e:
        raise RuntimeError(f'failed to render SVG to cairo context: {e}') from e

    # Extract the path from the cairo context. copy_path() preserves curves
    # when available; copy_path_flat() flattens to line segments.
    try:
        cpath = ctx.copy_path()
    except Exception:
        try:
            cpath = ctx.copy_path_flat()
        except Exception as e:
            raise RuntimeError(f'failed to extract cairo path: {e}') from e

    # Convert cairo.Path to skia.Path
    skia_path = skia.Path()
    # cairo.Path has attribute .data which is a sequence of (type, points)
    try:
        data = getattr(cpath, 'data', None) or cpath
        for el in data:
            # el is a tuple-like: (type, points)
            t = el[0]
            pts = el[1]
            # pycairo defines types on cairo.Path
            if t == cairo.PATH_MOVE_TO:
                skia_path.moveTo(float(pts[0][0]), float(pts[0][1]))
            elif t == cairo.PATH_LINE_TO:
                skia_path.lineTo(float(pts[0][0]), float(pts[0][1]))
            elif t == cairo.PATH_CURVE_TO:
                # curve_to typically contains three points: (x1,y1),(x2,y2),(x3,y3)
                try:
                    x1, y1 = pts[0]
                    x2, y2 = pts[1]
                    x3, y3 = pts[2]
                    skia_path.cubicTo(float(x1), float(y1), float(x2), float(y2), float(x3), float(y3))
                except Exception:
                    # Fallback: if pts is a flat tuple
                    if len(pts) >= 6:
                        skia_path.cubicTo(float(pts[0]), float(pts[1]), float(pts[2]), float(pts[3]), float(pts[4]), float(pts[5]))
            elif t == cairo.PATH_CLOSE_PATH:
                skia_path.close()
            else:
                # Unknown element type; ignore
                pass
    except Exception as e:
        raise RuntimeError(f'failed to convert cairo path to skia.Path: {e}') from e

    # If the converted skia.Path is empty, fail fast: this loader only
    # provides vector extraction (no raster fallback). Callers should use
    # an alternate path (e.g. direct librsvg rasterization) if they need a
    # raster image.
    try:
        empty = skia_path.isEmpty()
    except Exception:
        empty = False

    if empty:
        raise RuntimeError('failed to extract vector path from cairo (no vector geometry available)')

    # Wrap in a PCShape-like object compatible with the replayer
    class PCShape:
        def __init__(self, skia_paths: List[skia.Path]):
            self.skia_paths = skia_paths
            self.paths = [{'path_cmds': None, 'style': {}} for _ in skia_paths]

        def enable_style(self):
            return None

        def disable_style(self):
            return None

    return PCShape([skia_path])
