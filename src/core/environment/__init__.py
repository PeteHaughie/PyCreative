"""Thin re-export of environment helpers.

Implementation details live in `settings` and `window` submodules so importing
`core.environment` stays lightweight.
"""
from .settings import (  # noqa: F401
    delay,
    display_density,
    display_height,
    display_width,
    frame_count,
    frame_rate,
    height,
    pixel_density,
    pixel_height,
    pixel_width,
    settings,
    size,
    width,
)
from .window import (  # noqa: F401
    cursor,
    fullscreen,
    no_cursor,
    window_move,
    window_moved,
    window_ratio,
    window_resizeable,
    window_resized,
    window_title,
)

__all__ = [
    # settings
    'size',
    'settings',
    'frame_count',
    'frame_rate',
    'delay',
    'display_width',
    'display_height',
    'width',
    'height',
    'pixel_density',
    'pixel_width',
    'pixel_height',
    'display_density',
    'focused',
    # window
    'fullscreen',
    'cursor',
    'no_cursor',
    'window_move',
    'window_moved',
    'window_ratio',
    'window_resizeable',
    'window_resized',
    'window_title',
]
