"""Top-level package for pycreative.

This module exposes a small surface API but avoids importing heavy
dependencies (like pygame) at import-time. Consumers can still do
``from pycreative import Sketch``; the actual import is deferred until
the attribute is accessed.
"""

__all__ = ["Sketch", "input"]


def __getattr__(name: str):
	"""Lazily import attributes to avoid side-effects at import time.

	This uses PEP 562 module __getattr__ so `import pycreative` is cheap.
	"""
	import importlib

	if name == "Sketch":
		_mod = importlib.import_module(f"{__name__}.app")
		return getattr(_mod, "Sketch")
	if name == "input":
		_mod = importlib.import_module(f"{__name__}.input")
		return _mod
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
	return sorted(list(__all__))
