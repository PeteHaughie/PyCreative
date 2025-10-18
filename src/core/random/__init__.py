"""Thin re-export for core.random helpers.

Implementations live in `core.random.ops` to keep package import lightweight.
"""
from __future__ import annotations

# Re-export public functions for backwards compatibility
from .ops import (
    random,
    random_seed,
    random_gaussian,
    uniform,
    noise,
    noise_seed,
    noise_detail,
)

__all__ = [
    "random",
    "random_seed",
    "random_gaussian",
    "uniform",
    "noise",
    "noise_seed",
    "noise_detail",
]
