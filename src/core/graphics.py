"""Graphics helpers.

This module exposes a small helper used by tests to attach a Skia surface to a
pygame-like surface. The real implementation will integrate skia-python and
pygame; the current helper is minimal to drive TDD and tests.
"""

from typing import Any, Optional


def attach_skia_to_pygame(pygame_surface: Any, width: int = 640, height: int = 480, *, adapter: Optional[Any] = None) -> Optional[Any]:
	"""Create and attach a Skia surface for the given pygame surface.

	Adapter injection:
	- Prefer passing an `adapter` object with a `MakeSurface(info)` callable (useful for tests).
	- When `adapter` is None, the function will import `src.core.adapters.skia_adapter` which is the module responsible
	  for importing the real `skia` library.

	Raises ImportError when no adapter is available or when the adapter cannot access skia.
	"""
	# If an adapter is provided (test-friendly), use it directly.
	if adapter is not None:
		if hasattr(adapter, "MakeSurface"):
			info = {"width": width, "height": height}
			return adapter.MakeSurface(info)
		raise RuntimeError("Provided adapter does not implement MakeSurface")

	# Otherwise import the adapter module (adapter is the only place that imports skia).
	try:
		from src.core.adapters import skia_adapter as _adapter  # type: ignore
	except Exception as exc:
		raise ImportError("skia adapter is required to attach a skia surface") from exc

	info = {"width": width, "height": height}
	return _adapter.MakeSurface(info)
