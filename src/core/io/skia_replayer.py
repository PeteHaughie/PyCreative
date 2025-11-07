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
import json

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

    # Delegate to the centralized defensive replayer implementation. The
    # engine may record nested 'offscreen' ops whose payload is a list of
    # inner ops (stored under args['ops']). Some callers (presenters) handle
    # offscreen by unpacking those nested ops; when running the headless
    # skia replayer we should flatten any such nested ops so the central
    # replayer sees a flat list of operations it understands (rect, circle,
    # etc.). This keeps behavior consistent across presenters and the CLI.
    try:
        # prefer the implementation module directly
        from core.io.replay_to_skia_impl import replay_to_skia_canvas

        recorded = getattr(getattr(engine, 'graphics', None), 'commands', []) or []
        flat: list[dict] = []
        for cmd in recorded:
            # defensive checks and flattening
            if isinstance(cmd, dict) and cmd.get('op') == 'offscreen':
                args = cmd.get('args', {}) or {}
                inner_ops = args.get('ops') or []
                for inner in list(inner_ops):
                    if not isinstance(inner, dict):
                        continue
                    opn = inner.get('op')
                    inner_args = {k: v for k, v in inner.items() if k != 'op'}
                    flat.append({'op': opn, 'args': inner_args, 'meta': cmd.get('meta', {})})
                continue
            flat.append(cmd)

        # DEBUG: dump the flattened commands to /tmp for inspection during
        # headless runs. This is temporary and safe to leave in while
        # diagnosing missing primitives.
        try:
            # Sanitize the flattened command structure so we don't try to
            # JSON-serialize objects like PCGraphics or engine refs that may
            # appear in 'meta' or other fields. Replace unknown objects with
            # their repr() so the dump is still useful for debugging.
            def _safe(o):
                if isinstance(o, (str, int, float, bool)) or o is None:
                    return o
                if isinstance(o, dict):
                    out = {}
                    for k, v in o.items():
                        try:
                            if k in ('image', 'image_bytes'):
                                out[str(k)] = '<redacted-image>'
                            else:
                                out[str(k)] = _safe(v)
                        except Exception:
                            try:
                                out[str(k)] = repr(v)
                            except Exception:
                                out[str(k)] = f"<{type(v).__name__}>"
                    return out
                if isinstance(o, (list, tuple)):
                    return [_safe(x) for x in o]
                try:
                    return repr(o)
                except Exception:
                    return f"<{type(o).__name__}>"

            safe_flat = _safe(flat)
            dump_path = '/tmp/pycreative_flat.json'
            with open(dump_path, 'w', encoding='utf8') as fh:
                json.dump(safe_flat, fh, indent=2, ensure_ascii=False)
            logger.debug('replay_to_image_skia: dumped flattened commands to %s', dump_path)
        except Exception:
            logger.exception('replay_to_image_skia: failed to dump flattened commands')

        try:
            replay_to_skia_canvas(flat, c)
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
