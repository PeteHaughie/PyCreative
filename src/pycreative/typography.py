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
from typing import List, Optional

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

        # Compute alignment-adjusted coordinates for headless recording so
        # replayers that draw the recorded x/y directly match the sketch's
        # expected alignment.
        try:
            ax, ay = getattr(eng, 'current_text_align', (None, None)) or (None, None)
            ax = (ax or 'LEFT').upper()
            ay = (ay or 'BASELINE').upper()
        except Exception:
            ax = 'LEFT'
            ay = 'BASELINE'

        # Best-effort measurements (these may delegate to engine implementations)
        try:
            w = float(text_width(s))
        except Exception:
            w = None
        try:
            a = float(text_ascent())
        except Exception:
            a = None
        try:
            d = float(text_descent())
        except Exception:
            d = None

        adj_x = float(x)
        adj_y = float(y)
        # Horizontal
        try:
            if w is not None:
                if ax == 'CENTER':
                    adj_x = float(x) - (w / 2.0)
                elif ax == 'RIGHT':
                    adj_x = float(x) - float(w)
                else:
                    adj_x = float(x)
        except Exception:
            adj_x = float(x)

        # Vertical: assume ascent/descent measurements where possible.
        try:
            if ay == 'TOP':
                if a is not None:
                    adj_y = float(y) + float(a)
            elif ay == 'CENTER':
                if a is not None and d is not None:
                    adj_y = float(y) + ((float(a) - float(d)) / 2.0)
            elif ay == 'BOTTOM':
                if d is not None:
                    adj_y = float(y) - float(d)
            else:
                # BASELINE or unknown: keep as-is
                adj_y = float(y)
        except Exception:
            adj_y = float(y)

        # Also record into the engine graphics buffer when available so
        # headless replayers that read `engine.graphics.commands` see text
        # operations (this mirrors core.typography.text behaviour). Record
        # the adjusted coordinates but preserve the original as orig_x/orig_y
        # so test inspection can still see the passed values.
        try:
            g = getattr(eng, 'graphics', None)
            if g is not None:
                try:
                    # Include the current font size when recording so
                    # headless replayers can render text at the expected
                    # scale. Use engine.current_font_size when available.
                    font_size = getattr(eng, 'current_font_size', None)
                    g_args = dict(text=str(s), x=float(adj_x), y=float(adj_y), args=args, kwargs=kwargs, orig_x=float(x), orig_y=float(y))
                    if font_size is not None:
                        try:
                            g_args['font_size'] = float(font_size)
                        except Exception:
                            pass
                    # Also persist measured metrics when available so replayers
                    # don't need to recompute them.
                    try:
                        if w is not None:
                            g_args['text_width'] = float(w)
                    except Exception:
                        pass
                    try:
                        if a is not None:
                            g_args['text_ascent'] = float(a)
                    except Exception:
                        pass
                    try:
                        if d is not None:
                            g_args['text_descent'] = float(d)
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


def text_align(align_x: str, align_y: Optional[str] = None) -> None:
    """Set the current horizontal and optional vertical text alignment.

    This prefers to delegate to the engine's high-level API. When no
    engine implementation is available the function stores the chosen
    alignment on the engine object so headless tests and replayers can
    inspect it. Values are normalised to upper-case strings. If the
    vertical alignment is omitted, "BASELINE" is used per the public
    API.
    """
    handled = _try_delegate('text_align', align_x, align_y)
    if handled is not None:
        return handled
    try:
        ax = (align_x or '').upper() if align_x is not None else ''
    except Exception:
        ax = ''
    try:
        ay = (align_y or 'BASELINE').upper() if align_y is not None else 'BASELINE'
    except Exception:
        ay = 'BASELINE'

    # Validate common tokens; fall back to defaults when unknown
    if ax not in ('LEFT', 'CENTER', 'RIGHT'):
        ax = 'LEFT'
    if ay not in ('TOP', 'BOTTOM', 'CENTER', 'BASELINE'):
        ay = 'BASELINE'

    try:
        eng = _get_engine()
        setattr(eng, 'current_text_align', (ax, ay))
        # Also mirror into separate attributes for convenience
        setattr(eng, 'current_text_align_x', ax)
        setattr(eng, 'current_text_align_y', ay)
        # Record into graphics if present so replayers see alignment
        try:
            g = getattr(eng, 'graphics', None)
            if g is not None:
                try:
                    g.record('text_align', align_x=ax, align_y=ay)
                except Exception:
                    pass
        except Exception:
            pass
    except Exception:
        pass


__all__ = [
    'PCFont', 'load_font', 'text_font', 'text_size', 'text',
    'text_width', 'text_ascent', 'text_descent', 'text_align',
]
