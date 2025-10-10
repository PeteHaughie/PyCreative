from typing import Optional, Sequence
try:
    import skia
    _HAS_SKIA = True
except Exception:
    skia = None  # type: ignore
    _HAS_SKIA = False


def make_dash(path_intervals: Sequence[float], phase: float = 0.0):
    """Best-effort PathEffect dash factory across skia-python builds.

    Returns a skia.PathEffect-like object or None when unsupported.
    """
    if not _HAS_SKIA:
        return None
    if not path_intervals:
        return None
    # try common variants
    try:
        # common API
        pe = skia.PathEffect.MakeDash(list(path_intervals), float(phase))
        if pe is not None:
            return pe
    except Exception:
        pass
    # some builds may expose PathEffect as a class with MakeDash
    try:
        PathEffect = getattr(skia, 'PathEffect', None)
        if PathEffect is not None and hasattr(PathEffect, 'MakeDash'):
            pe = PathEffect.MakeDash(list(path_intervals), float(phase))
            return pe
    except Exception:
        pass
    # last-ditch: some variants expose skia.DashPathEffect or similar
    try:
        maker = getattr(skia, 'DashPathEffect', None)
        if maker:
            return maker(list(path_intervals), float(phase))
    except Exception:
        pass
    return None
