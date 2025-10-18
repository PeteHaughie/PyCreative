"""Color utilities used across core packages.

Keep pure, side-effect-free conversion helpers here so tests can import
them without pulling in engine internals.
"""
# Re-export small, pure conversion helpers from dedicated modules
from core.color.hsb_to_rgb import hsb_to_rgb
from core.color.rgb_to_hsb import rgb_to_hsb
from core.color.ops import (
    color,
    red,
    green,
    blue,
    alpha,
    lerp_color,
)

__all__ = [
    'hsb_to_rgb',
    'rgb_to_hsb',
    'color',
    'red',
    'green',
    'blue',
    'alpha',
    'lerp_color',
]
