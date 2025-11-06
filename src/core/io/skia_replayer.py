"""Skia-based replayer: render recorded GraphicsBuffer commands into a
Skia CPU surface and write a PNG. This provides an authoritative Skia
snapshot for headless debugging when skia-python is available.

This module is defensive: it prefers the modern Skia Python API where
available and performs robust conversions when bindings differ across
platforms/versions.
"""
from __future__ import annotations

from typing import Any
import os
import logging

logger = logging.getLogger(__name__)


def replay_to_image_skia(engine: Any, path: str) -> None:
    """Render engine.graphics.commands into a Skia raster surface and write PNG.

    The target image size is taken from engine.width/engine.height.
    """
    try:
        import skia
    except Exception:
        logger.debug('replay_to_image_skia: skia not available')
        raise

    w = int(getattr(engine, 'width', 200))
    h = int(getattr(engine, 'height', 200))
    if w <= 0 or h <= 0:
        raise RuntimeError('invalid target size for skia replay')

    # Prefer a raster surface with N32 premultiplied format (portable)
    try:
        surf = skia.Surface.MakeRasterN32Premul(int(w), int(h))
    except Exception:
        try:
            # Older bindings may accept ImageInfo style
            info = skia.ImageInfo.Make(int(w), int(h), skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
            surf = skia.Surface.MakeRaster(info)
        except Exception:
            # Last resort: try the surface constructor (some builds expose this)
            surf = None
            try:
                surf = skia.Surface(int(w), int(h))
            except Exception:
                pass

    if surf is None:
        raise RuntimeError('Could not create a Skia raster surface')

    c = surf.getCanvas()

    # Default background: clear to opaque white unless a background op paints over it
    try:
        try:
            c.clear(skia.Color4f(1.0, 1.0, 1.0, 1.0))
        except Exception:
            c.clear(0xFFFFFFFF)
    except Exception:
        # non-fatal
        pass

    # Delegate to the centralized defensive replayer implementation
    try:
        # prefer the implementation module directly
        from core.io.replay_to_skia_impl import replay_to_skia_canvas
        try:
            replay_to_skia_canvas(getattr(getattr(engine, 'graphics', None), 'commands', []) or [], c)
        except Exception:
            logger.exception('replay_to_image_skia: error while replaying commands')
    except Exception:
        logger.exception('replay_to_image_skia: failed to import replay_to_skia_impl')

    # Snapshot and encode to PNG bytes
    img = surf.makeImageSnapshot()
    if img is None:
        raise RuntimeError('skia makeImageSnapshot returned None')

    try:
        data = img.encodeToData()
    except Exception:
        data = None
    if data is None:
        raise RuntimeError('skia encodeToData returned None')

    # extract bytes robustly
    b = None
    try:
        if hasattr(data, 'toBytes'):
            b = data.toBytes()
        elif hasattr(data, 'asBytes'):
            b = data.asBytes()
        elif hasattr(data, 'tobytes'):
            b = data.tobytes()
        else:
            b = bytes(data)
    except Exception:
        b = None

    if not b:
        raise RuntimeError('Could not extract PNG bytes from skia.Data')

    # Ensure parent directory exists
    try:
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
    except Exception:
        pass

    with open(path, 'wb') as f:
        f.write(b)
    logger.debug('replay_to_image_skia: wrote %s (%d bytes)', path, len(b))
