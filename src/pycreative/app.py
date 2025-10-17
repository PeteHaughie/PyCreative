"""Compatibility shim for older examples that import `from pycreative.app import Sketch`.

This module provides a minimal `Sketch` base class that example code can
subclass. It intentionally stays tiny to avoid import-time side-effects.

Newer code should import from `pycreative` or use the Engine-based APIs.
"""
from __future__ import annotations

# Minimal base class used by legacy examples. It exists so examples that
# `from pycreative.app import Sketch` can subclass without failing import.
class Sketch:
    """A tiny no-op base Sketch class for legacy examples to subclass."""
    pass

# Re-export commonly used shims from the package-level module for convenience
# (examples sometimes expect these at `pycreative.app`).
try:
    pass
except Exception:
    # Best-effort only; do not raise on import if the package-level functions
    # are not yet available during early import phases.
    pass
