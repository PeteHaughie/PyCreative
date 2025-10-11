"""Adapter module for skia.

All direct imports of the `skia` library should live here. Other modules should
depend on this adapter rather than importing `skia` directly.
"""
try:
    import skia  # type: ignore
except Exception as exc:  # pragma: no cover - adapter will be patched in tests
    skia = None  # type: ignore


def MakeSurface(info: dict):
    if skia is None:
        raise ImportError("skia is not available")
    # Real implementation would translate info into Skia image info and create surface
    # For now, call a MakeSurface-like factory if available on the skia import
    if hasattr(skia, "MakeSurface"):
        return skia.MakeSurface(info)
    # Fallback: return a simple dict to represent a surface
    return {"surface": True, **info}
