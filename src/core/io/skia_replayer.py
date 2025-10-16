"""Skia-based replayer: render recorded GraphicsBuffer commands into a
Skia CPU surface and write a PNG. This provides an authoritative Skia
snapshot for headless debugging when skia-python is available.
"""
    # mypy: ignore-errors
from __future__ import annotations

from typing import Any


def replay_to_image_skia(engine: Any, path: str) -> None:
    try:
        import skia
    except Exception:
        raise

    w = int(getattr(engine, 'width', 200))
    h = int(getattr(engine, 'height', 200))
    surf = skia.Surface(w, h)
    c = surf.getCanvas()

    # Default background
    try:
        c.clear(skia.Color4f(1.0, 1.0, 1.0, 1.0))
    except Exception:
        try:
            c.clear(0xFFFFFFFF)
        except Exception:
            pass

    for cmd in getattr(engine.graphics, 'commands', []):
        op = cmd.get('op')
        args = cmd.get('args', {})
        try:
            if op == 'background':
                r = float(args.get('r', 200)) / 255.0
                g = float(args.get('g', 200)) / 255.0
                b = float(args.get('b', 200)) / 255.0
                try:
                    c.clear(skia.Color4f(r, g, b, 1.0))
                except Exception:
                    c.clear(0xFF000000 | (int(r * 255) << 16) | (int(g * 255) << 8) | int(b * 255))
            elif op == 'rect':
                x = float(args.get('x', 0))
                y = float(args.get('y', 0))
                rw = float(args.get('w', 0))
                rh = float(args.get('h', 0))
                fill = args.get('fill')
                stroke = args.get('stroke')
                sw = float(args.get('stroke_weight', 1) or 1)
                if fill is not None:
                    p = skia.Paint()
                    p.setAntiAlias(True)
                    if isinstance(fill, (tuple, list)):
                        r, g, b = [float(v) / 255.0 for v in fill[:3]]
                        try:
                            p.setColor(skia.Color4f(r, g, b, 1.0))
                        except Exception:
                            p.setColor((int(r * 255) << 16) | (int(g * 255) << 8) | int(b * 255))
                    else:
                        v = float(fill) / 255.0
                        try:
                            p.setColor(skia.Color4f(v, v, v, 1.0))
                        except Exception:
                            p.setColor(int(v * 255))
                    c.drawRect(skia.Rect.MakeLTRB(x, y, x + rw, y + rh), p)
                if stroke is not None and sw > 0:
                    p = skia.Paint()
                    p.setStyle(skia.Paint.kStroke_Style)
                    p.setStrokeWidth(sw)
                    p.setAntiAlias(True)
                    if isinstance(stroke, (tuple, list)):
                        r, g, b = [float(v) / 255.0 for v in stroke[:3]]
                        try:
                            p.setColor(skia.Color4f(r, g, b, 1.0))
                        except Exception:
                            p.setColor((int(r * 255) << 16) | (int(g * 255) << 8) | int(b * 255))
                    else:
                        v = float(stroke) / 255.0
                        try:
                            p.setColor(skia.Color4f(v, v, v, 1.0))
                        except Exception:
                            p.setColor(int(v * 255))
                    c.drawRect(skia.Rect.MakeLTRB(x, y, x + rw, y + rh), p)
            elif op == 'line':
                x1 = float(args.get('x1', 0))
                y1 = float(args.get('y1', 0))
                x2 = float(args.get('x2', 0))
                y2 = float(args.get('y2', 0))
                sw = float(args.get('stroke_weight', 1) or 1)
                stroke = args.get('stroke', (0, 0, 0))
                p = skia.Paint()
                p.setAntiAlias(True)
                p.setStyle(skia.Paint.kStroke_Style)
                p.setStrokeWidth(sw)
                if isinstance(stroke, (tuple, list)):
                    r, g, b = [float(v) / 255.0 for v in stroke[:3]]
                    try:
                        p.setColor(skia.Color4f(r, g, b, 1.0))
                    except Exception:
                        p.setColor((int(r * 255) << 16) | (int(g * 255) << 8) | int(b * 255))
                else:
                    v = float(stroke) / 255.0
                    try:
                        p.setColor(skia.Color4f(v, v, v, 1.0))
                    except Exception:
                        p.setColor(int(v * 255))
                c.drawLine(x1, y1, x2, y2, p)
        except Exception:
            # Best-effort drawing; skip problematic commands instead of failing
            continue

    img = surf.makeImageSnapshot()
    data = img.encodeToData()
    if data is None:
        raise RuntimeError('skia encodeToData returned None')

    # convert to bytes robustly
    b = None
    if hasattr(data, 'toBytes'):
        try:
            b = data.toBytes()
        except Exception:
            b = None
    if b is None and hasattr(data, 'asBytes'):
        try:
            b = data.asBytes()
        except Exception:
            b = None
    if b is None:
        try:
            b = bytes(data)
        except Exception:
            b = None
    if b is None:
        raise RuntimeError('Could not extract PNG bytes from skia.Data')

    with open(path, 'wb') as f:
        f.write(b)
