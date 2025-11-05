"""Public typography shims for PyCreative.

These functions delegate to the current engine where possible. When the
engine doesn't provide a high-level text API the shims use lightweight
fallback behaviour so tests and headless examples can run.

The goal is to provide small, well-documented stubs that match the
project's public API used by examples/docs.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, List, Optional

from . import _get_engine


@dataclass
class PCFont:
    """Lightweight representation of a font used by the shims.

    Only stores the source filename/name and an optional size. Real
    rendering backends will provide a richer implementation; these
    helpers allow tests to inspect that a font was chosen.
    """

    name: str
    size: Optional[float] = None

    @staticmethod
    def list() -> List[str]:
        """Return a list of font names discovered on the system.

        Implementation is intentionally small: scan the common macOS
        font folders and return basenames (without extension). This
        keeps the function dependency-free while being useful for
        examples and tests.
        """
        paths = [
            '/Library/Fonts',
            '/System/Library/Fonts',
            os.path.expanduser('~/Library/Fonts'),
        ]
        names: List[str] = []
        exts = {'.ttf', '.otf', '.ttc'}
        for p in paths:
            try:
                for fn in os.listdir(p):
                    root, ext = os.path.splitext(fn)
                    if ext.lower() in exts:
                        names.append(root)
            except Exception:
                # Ignore missing dirs or permission issues
                continue
        # De-duplicate while preserving order
        seen = set()
        uniq: List[str] = []
        for n in names:
            if n not in seen:
                seen.add(n)
                uniq.append(n)
        return uniq


def _try_delegate(func_name: str, *args, **kwargs):
    """Attempt to call into a high-level engine API (SimpleSketchAPI).

    If delegation fails, return None so the caller can fall back to
    default behaviour.
    """
    eng = _get_engine()
    try:
        # Import lazily so test environments that don't have the
        # core package installed don't fail on import.
        from core.engine.api.simple import SimpleSketchAPI

        api = SimpleSketchAPI(eng)
        fn = getattr(api, func_name)
        return fn(*args, **kwargs)
    except Exception:
        return None


def load_font(filename: str, size: Optional[float] = None) -> PCFont:
    """Load a font and return a PCFont stub.

    This lightweight implementation does not perform full font parsing
    but stores the requested filename/name and size. Engines may replace
    this object with a richer representation when `text_font` is set.
    """
    # Try to delegate to engine first
    delegated = _try_delegate('load_font', filename, size)
    if delegated is not None:
        return delegated

    # Fallback: create a PCFont using the basename
    name = os.path.basename(filename)
    font = PCFont(name=name, size=size)
    # Persist on engine so replayers/presenters can inspect chosen font
    try:
        eng = _get_engine()
        setattr(eng, 'last_loaded_font', font)
    except Exception:
        pass
    return font


def text_font(font: PCFont, size: Optional[float] = None) -> None:
    """Set the active font for subsequent text calls.

    The call will prefer to delegate to a high-level engine API. When a
    simple engine is used, the font and size are stored on the engine
    object for tests and replayers to inspect.
    """
    handled = _try_delegate('text_font', font, size)
    if handled is not None:
        return handled
    try:
        eng = _get_engine()
        eng.current_font = font
        if size is not None:
            eng.current_font.size = size
            eng.current_font_size = size
        else:
            eng.current_font_size = getattr(font, 'size', None)
    except Exception:
        pass


def text_size(size: float) -> None:
    """Set the size for the current font."""
    handled = _try_delegate('text_size', size)
    if handled is not None:
        return handled
    try:
        eng = _get_engine()
        eng.current_font_size = float(size)
        if hasattr(eng, 'current_font') and eng.current_font is not None:
            eng.current_font.size = float(size)
    except Exception:
        pass


def text(s: str, x: float, y: float, *args, **kwargs) -> None:
    """Draw text using the engine if available; otherwise persist
    the last text drawn for tests.
    """
    handled = _try_delegate('text', s, x, y, *args, **kwargs)
    if handled is not None:
        return handled
    try:
        eng = _get_engine()
        # Store a simple record so headless tests can assert text calls
        last = getattr(eng, 'last_text_calls', [])
        last.append({'text': s, 'x': x, 'y': y, 'args': args, 'kwargs': kwargs})
        eng.last_text_calls = last
        # Also record into the engine graphics buffer when available so
        # headless replayers that read `engine.graphics.commands` see text
        # operations (this mirrors core.typography.text behaviour).
        try:
            g = getattr(eng, 'graphics', None)
            if g is not None:
                try:
                    # Include the current font size when recording so
                    # headless replayers can render text at the expected
                    # scale. Use engine.current_font_size when available.
                    font_size = getattr(eng, 'current_font_size', None)
                    g_args = dict(text=str(s), x=float(x), y=float(y), args=args, kwargs=kwargs)
                    if font_size is not None:
                        try:
                            g_args['font_size'] = float(font_size)
                        except Exception:
                            pass
                    g.record('text', **g_args)
                except Exception:
                    pass
        except Exception:
            pass
    except Exception:
        pass


def text_width(s: str) -> float:
    """Return an approximate width for the string using the current
    font size. Engines should provide a precise implementation.
    """
    delegated = _try_delegate('text_width', s)
    if delegated is not None:
        return float(delegated)
    try:
        eng = _get_engine()
        size = getattr(eng, 'current_font_size', None) or 12.0
    except Exception:
        size = 12.0
    # Simple monospace-ish approximation: width per character = 0.6 * size
    return float(len(s) * (0.6 * float(size)))


def text_ascent() -> float:
    delegated = _try_delegate('text_ascent')
    if delegated is not None:
        return float(delegated)
    try:
        eng = _get_engine()
        size = getattr(eng, 'current_font_size', 12.0)
    except Exception:
        size = 12.0
    return float(0.8 * float(size))


def text_descent() -> float:
    delegated = _try_delegate('text_descent')
    if delegated is not None:
        return float(delegated)
    try:
        eng = _get_engine()
        size = getattr(eng, 'current_font_size', 12.0)
    except Exception:
        size = 12.0
    return float(0.2 * float(size))


__all__ = [
    'PCFont', 'load_font', 'text_font', 'text_size', 'text',
    'text_width', 'text_ascent', 'text_descent',
]
