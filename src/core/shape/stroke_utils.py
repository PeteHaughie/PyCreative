"""Utilities to map public stroke cap/join names to Skia constants.

This central mapping ensures the API constants used in docs (ROUND,
SQUARE, PROJECT, MITER, BEVEL) map deterministically to the Skia
Paint constants available at runtime.
"""
from __future__ import annotations

from typing import Any

def map_stroke_cap(skia_module: Any, cap_name: str):
    if cap_name is None:
        return None
    name = str(cap_name).upper()
    # Processing-style mapping: PROJECT -> Skia kSquare_Cap (projecting),
    # SQUARE -> Skia kButt_Cap (no extension), ROUND -> kRound_Cap.
    if name == 'PROJECT':
        return getattr(skia_module.Paint, 'kSquare_Cap')
    if name == 'SQUARE':
        return getattr(skia_module.Paint, 'kButt_Cap')
    if name == 'ROUND':
        return getattr(skia_module.Paint, 'kRound_Cap')
    # allow direct numeric passthrough
    try:
        return int(cap_name)
    except Exception:
        return None


def map_stroke_join(skia_module: Any, join_name: str):
    if join_name is None:
        return None
    name = str(join_name).upper()
    if name == 'MITER':
        return getattr(skia_module.Paint, 'kMiter_Join')
    if name == 'BEVEL':
        return getattr(skia_module.Paint, 'kBevel_Join')
    if name == 'ROUND':
        return getattr(skia_module.Paint, 'kRound_Join')
    try:
        return int(join_name)
    except Exception:
        return None
