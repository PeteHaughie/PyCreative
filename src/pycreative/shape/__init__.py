"""Shape package shim — exposes PShape and load_svg at package level.

This keeps the previous import path `pycreative.shape` working while
the implementation is split across modules.
"""
from .core import PShape
from .loader import load_svg

__all__ = ["PShape", "load_svg"]

# Backwards-compatible alias used by older callers
def load_shape_from_file(path: str):
	return load_svg(path)

