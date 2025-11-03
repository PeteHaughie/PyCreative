"""Top-level public shims for the `pycreative` package.

This module exposes a tiny runtime surface consumed by examples and tests:
- current engine getters/setters used by public helper modules
- a small set of public constants (PROJECT/SQUARE/ROUND/MITER/BEVEL)

Keep this module small and import-safe.
"""
from __future__ import annotations

from typing import Any, Optional

# Public stroke/shape constants (Processing-style names)
PROJECT = 'PROJECT'
SQUARE = 'SQUARE'
ROUND = 'ROUND'
MITER = 'MITER'
BEVEL = 'BEVEL'

# Current engine storage used by public helper shims. Tests and presenters
# call `pycreative.set_current_engine(engine)` during unit tests to provide
# a lightweight stub that the public functions can call into.
_CURRENT_ENGINE: Optional[Any] = None


def set_current_engine(engine: Any) -> None:
    global _CURRENT_ENGINE
    _CURRENT_ENGINE = engine


def get_current_engine() -> Optional[Any]:
    return _CURRENT_ENGINE


def _get_engine() -> Any:
    """Internal helper used by public shims that need an engine instance.

    Returns the currently-set engine or raises a helpful error when none
    is configured (tests typically call `set_current_engine` first).
    """
    if _CURRENT_ENGINE is None:
        raise RuntimeError('no current engine configured; call set_current_engine(engine)')
    return _CURRENT_ENGINE


def _reset_current_engine() -> None:
    """Test helper: reset the stored engine."""
    global _CURRENT_ENGINE
    _CURRENT_ENGINE = None


__all__ = [
    'PROJECT', 'SQUARE', 'ROUND', 'MITER', 'BEVEL',
    'set_current_engine', 'get_current_engine', '_get_engine', '_reset_current_engine',
]
