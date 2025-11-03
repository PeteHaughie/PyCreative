"""pycreative.shape package exports and helpers.

Prefer the svg.py-backed loader when available; fall back to the
conservative XML loader otherwise.
"""
from __future__ import annotations

try:
	# Prefer a skia-backed loader when available for highest-fidelity SVG
	# rendering. Fall back to the svgpy loader or the conservative XML loader.
	from .skia_svg_adapter import load_shape, load_svg
except Exception:
	try:
		from .svgpy_loader import load_shape, load_svg
	except Exception:
		from .loader import load_shape, load_svg

__all__ = ["load_shape", "load_svg"]
