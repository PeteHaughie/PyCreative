"""SVG loader backed by svg.py when available.

This module provides a drop-in replacement for the previous Cairo-based
loader. It prefers to use the `svg` package (svg.py) when available and
falls back to the conservative XML loader if not. The intent is to keep
SVG parsing standards-complete without heavy native dependencies.

Currently this prototype delegates to the existing XML loader for parsing
and returns the same `PCShape` object. When desired we can extend this
module to use the `svg` package APIs to resolve <use>/<defs> and CSS
more accurately; the shape conversion logic will live here.
"""
from __future__ import annotations

from typing import Any

try:
    # svg.py package (optional)
    import svg  # type: ignore
except Exception:
    svg = None  # type: ignore

from .loader import load_svg as _xml_load_svg


def load_svg(path: str) -> Any:
    """Load an SVG and return a PCShape-like object.

    If the `svg` package is present we may use it for enhanced parsing in
    the future; today we delegate to the conservative XML loader to keep
    behaviour stable. This wrapper provides a single migration point.
    """
    # If svg.py is available we could parse and pre-process the DOM here.
    # For now delegate to the robust XML loader and return its result.
    return _xml_load_svg(path)


def load_shape(path: str) -> Any:
    # compatibility alias
    return load_svg(path)
