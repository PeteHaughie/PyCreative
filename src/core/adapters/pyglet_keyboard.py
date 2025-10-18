"""Lightweight adapter to normalize pyglet keyboard events to the engine's
internal event shape.

Follows the same lazy-import pattern as `pyglet_mouse.py` so tests and
headless runs don't require pyglet. Exposes helpers to map pyglet key
constants to our `key`/`key_code` semantics and produces a small event
dict the Engine can consume.
"""
# mypy: ignore-errors
import re
from typing import Any, Dict, Optional


def _load_pyglet():
    try:
        import pyglet
        return pyglet
    except Exception:
        return None


def _map_key_constant(py_key: Any) -> Optional[str]:
    """Map common pyglet key constants (printable or named) to our key string.

    For printable ASCII keys we prefer the single-character string (e.g. 'a').
    For special keys return names like 'LEFT', 'RIGHT', 'BACKSPACE', 'ENTER', etc.
    If pyglet is not available return None.
    """
    pyglet = _load_pyglet()
    if pyglet is None:
        return None
    try:
        from pyglet.window import key as _k
        # Check common printable keys: pyglet uses integer keycodes for named keys
        # For named special keys, try mapping to an uppercase name
        for attr in dir(_k):
            try:
                if getattr(_k, attr) != py_key:
                    continue
            except Exception:
                continue
            # Some key names in pyglet may include trailing underscores to
            # avoid Python keyword conflicts (e.g. 'return_'). Strip trailing
            # underscores so callers get the canonical name.
            attr_clean = attr.rstrip('_') if isinstance(attr, str) else attr
            if isinstance(attr_clean, str):
                # If the attribute name encodes a digit (e.g. 'NUM_1' or 'KP_1'),
                # return the digit as the printable key value.
                m = re.search(r"(\d+)$", attr_clean)
                if m:
                    return m.group(1)
                # Single-character names (unlikely for pyglet attr names)
                # should be returned as lowercase printable chars.
                if len(attr_clean) == 1:
                    return attr_clean.lower()
                # Return canonical uppercase name for other special keys
                return attr_clean.upper()
    except Exception:
        pass
    return None


def normalize_event(event: Any) -> Dict[str, Any]:
    """Normalize a pyglet key event or an already-shaped dict into a plain dict.

    The returned dict contains at least these keys:
      - 'key': a printable character or special-name string when available
      - 'key_code': a fallback code (e.g. 'LEFT', 'F1') when the key isn't printable
      - 'modifiers': a set-like list of modifier names (e.g. ['SHIFT', 'CTRL'])
      - 'repeat': boolean indicating a repeated key event if available

    The function is defensive and will return sensible defaults when pyglet
    isn't installed or when a plain dict is passed through.
    """
    if event is None:
        return {}

    # If it's already a mapping, make a shallow copy and continue to normalize
    try:
        if isinstance(event, dict):
            out = dict(event)
        else:
            out = {}
    except Exception:
        out = {}
    try:
        # Try to compute 'key' from pyglet event attributes. Support both
        # event-like objects and dicts that contain 'symbol'/'key'/'string'.
        py_key = None
        if isinstance(event, dict):
            py_key = event.get('symbol', event.get('key', None))
        else:
            py_key = getattr(event, 'symbol', getattr(event, 'key', None))

        mapped = _map_key_constant(py_key)
        # If the caller provided an explicit 'key' or 'key_code' in a dict, preserve them
        explicit_key = None
        explicit_key_code = None
        if isinstance(event, dict):
            explicit_key = event.get('key', None) if 'key' in event else None
            explicit_key_code = event.get('key_code', None) if 'key_code' in event else None

        if mapped is not None:
            # Printable single-character keys become the `key` value
            if len(mapped) == 1:
                out['key'] = mapped.lower()
                out['key_code'] = None if explicit_key_code is None else explicit_key_code
            else:
                # Special keys are exposed via `key_code`; `key` should be None
                out['key'] = None if explicit_key is None else explicit_key
                out['key_code'] = mapped if explicit_key_code is None else explicit_key_code
                # If no explicit printable key exists, expose Processing-style
                # sentinel so sketches can test for coded keys via `self.key == 'CODED'`.
                # If the explicit key_code encodes a digit (e.g., 'NUM_1' or 'KP_1'),
                # treat it as a printable digit key.
                if out['key'] is None and out.get('key_code') is not None:
                    maybe = out.get('key_code')
                    try:
                        m = re.search(r"(\d+)$", str(maybe))
                        if m:
                            out['key'] = m.group(1)
                            out['key_code'] = None
                        else:
                            out['key'] = 'CODED'
                    except Exception:
                        out['key'] = 'CODED'
        else:
            # If caller explicitly gave a key, preserve it
            if explicit_key is not None:
                out['key'] = explicit_key
                out['key_code'] = explicit_key_code
            else:
                # If py_key is a printable string (e.g., 'a') use it
                if isinstance(py_key, str) and len(py_key) == 1:
                    out['key'] = py_key.lower()
                    out['key_code'] = explicit_key_code
                else:
                    # Fallback to 'string' attribute or dict key if present
                    s = event.get('string') if isinstance(event, dict) else getattr(event, 'string', None)
                    out['key'] = s if s is not None else (event.get('key') if isinstance(event, dict) else getattr(event, 'key', None))
                    # Preserve explicit key_code if present, otherwise derive if possible
                    if explicit_key_code is not None:
                        out['key_code'] = explicit_key_code
                    else:
                        out['key_code'] = None if s else (event.get('key') if isinstance(event, dict) else getattr(event, 'key', None))
                    # If we've derived a key_code but no printable key, surface 'CODED'
                    if out.get('key') is None and out.get('key_code') is not None:
                        try:
                            m = re.search(r"(\d+)$", str(out.get('key_code')))
                            if m:
                                out['key'] = m.group(1)
                                out['key_code'] = None
                            else:
                                out['key'] = 'CODED'
                        except Exception:
                            out['key'] = 'CODED'
    except Exception:
        out['key'] = None
        out['key_code'] = None

    # Modifiers: pyglet provides modifiers as an int mask sometimes
    try:
        mods = getattr(event, 'modifiers', None)
        if mods is None:
            out['modifiers'] = []
        else:
            # Lazy-load pyglet to interpret masks; if not available, return raw value
            pyglet = _load_pyglet()
            if pyglet is not None:
                from pyglet.window import key as _k
                flags = []
                if mods & getattr(_k, 'MOD_SHIFT', 0):
                    flags.append('SHIFT')
                if mods & getattr(_k, 'MOD_CTRL', 0):
                    flags.append('CTRL')
                if mods & getattr(_k, 'MOD_ALT', 0):
                    flags.append('ALT')
                out['modifiers'] = flags
            else:
                out['modifiers'] = [mods]
    except Exception:
        out['modifiers'] = []

    try:
        out['repeat'] = bool(getattr(event, 'repeat', False))
    except Exception:
        out['repeat'] = False

    return out
