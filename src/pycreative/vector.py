"""Expose the project's PCVector type for external imports.

This module intentionally does NOT provide a `PVector` compatibility alias.
Exporting `PCVector` encourages port authors to consciously adopt the
PyCreative vector type and avoids accidental reliance on Processing's
naming and semantics.
"""
from __future__ import annotations

from core.math import PCVector

__all__ = ["PCVector"]
