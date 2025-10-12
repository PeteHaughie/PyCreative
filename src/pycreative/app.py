"""Compatibility shim exposing `Sketch` for legacy examples.

This tries to import the legacy Sketch implementation from `src_old.pycreative`.
If that fails, it leaves a lightweight fallback Sketch to avoid import errors
in tests (the fallback is intentionally minimal).
"""
try:
    # Preferred: legacy implementation in src_old
    from src_old.pycreative.app import Sketch  # type: ignore
except Exception:
    try:
        # Fallback: if installed package exists
        from pycreative.app import Sketch  # type: ignore
    except Exception:
        # Minimal fallback Sketch stub to avoid import errors in tests.
        class Sketch:
            def __init__(self, *args, **kwargs):
                self.width = 640
                self.height = 480

            def setup(self):
                return None

            def draw(self):
                return None

            def size(self, w, h, fullscreen=False):
                self.width = w
                self.height = h

__all__ = ["Sketch"]
