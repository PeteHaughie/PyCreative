"""Compatibility shim for the relocated `shape` package.

This module re-exports the public API from the package-based
implementation at `pycreative.shape` so existing imports continue to work.
"""
from __future__ import annotations

# Re-export from the package implementation (the package lives at src/pycreative/shape/)
from .shape import PShape, load_svg, load_shape_from_file  # type: ignore

__all__ = ["PShape", "load_svg", "load_shape_from_file"]
