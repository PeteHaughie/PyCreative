"""Replay recorded GraphicsBuffer commands onto a Skia Canvas.

This small helper mirrors the Pillow replayer but issues Skia draw calls
so the engine can render recorded commands into a Skia Surface (CPU or
GPU-backed) for presentation.
"""
from __future__ import annotations

from typing import Any


def replay_to_skia_canvas(commands: list, canvas: Any) -> None:
    try:
        import skia
    except Exception:
        raise

    for cmd in commands:
        op = cmd.get('op')
        args = cmd.get('args', {})
        try:
            if op == 'background':
                r = int(args.get('r', 200))
                g = int(args.get('g', 200))
                b = int(args.get('b', 200))
                try:
                    canvas.clear(skia.Color4f(r/255.0, g/255.0, b/255.0, 1.0))
                except Exception:
                    canvas.clear((0xFF << 24) | (r << 16) | (g << 8) | b)
            elif op == 'rect':
                x = float(args.get('x', 0))
                y = float(args.get('y', 0))
                w = float(args.get('w', 0))
                h = float(args.get('h', 0))
                fill = args.get('fill')
                stroke = args.get('stroke')
                sw = float(args.get('stroke_weight', 1) or 1)
                if fill is not None:
                    p = skia.Paint()
                    p.setAntiAlias(True)
                    if isinstance(fill, (tuple, list)):
                        r, g, b = [float(v)/255.0 for v in fill[:3]]
                        try:
                            p.setColor(skia.Color4f(r, g, b, 1.0))
                        except Exception:
                            p.setColor((int(r*255)<<16)|(int(g*255)<<8)|int(b*255))
                    else:
                        v = float(fill)/255.0
                        try:
                            p.setColor(skia.Color4f(v, v, v, 1.0))
                        except Exception:
                            p.setColor(int(v*255))
                    canvas.drawRect(skia.Rect.MakeLTRB(x, y, x + w, y + h), p)
                if stroke is not None and sw > 0:
                    p = skia.Paint()
                    p.setStyle(skia.Paint.kStroke_Style)
                    p.setStrokeWidth(sw)
                    p.setAntiAlias(True)
                    if isinstance(stroke, (tuple, list)):
                        r, g, b = [float(v)/255.0 for v in stroke[:3]]
                        try:
                            p.setColor(skia.Color4f(r, g, b, 1.0))
                        except Exception:
                            p.setColor((int(r*255)<<16)|(int(g*255)<<8)|int(b*255))
                    else:
                        v = float(stroke)/255.0
                        try:
                            p.setColor(skia.Color4f(v, v, v, 1.0))
                        except Exception:
                            p.setColor(int(v*255))
                    canvas.drawRect(skia.Rect.MakeLTRB(x, y, x + w, y + h), p)
            elif op == 'line':
                x1 = float(args.get('x1', 0))
                y1 = float(args.get('y1', 0))
                x2 = float(args.get('x2', 0))
                y2 = float(args.get('y2', 0))
                sw = float(args.get('stroke_weight', 1) or 1)
                stroke = args.get('stroke', (0,0,0))
                p = skia.Paint()
                p.setAntiAlias(True)
                p.setStyle(skia.Paint.kStroke_Style)
                p.setStrokeWidth(sw)
                if isinstance(stroke, (tuple, list)):
                    r, g, b = [float(v)/255.0 for v in stroke[:3]]
                    try:
                        p.setColor(skia.Color4f(r, g, b, 1.0))
                    except Exception:
                        p.setColor((int(r*255)<<16)|(int(g*255)<<8)|int(b*255))
                else:
                    v = float(stroke)/255.0
                    try:
                        p.setColor(skia.Color4f(v, v, v, 1.0))
                    except Exception:
                        p.setColor(int(v*255))
                canvas.drawLine(x1, y1, x2, y2, p)
        except Exception:
            # best-effort: ignore commands that fail to draw
            continue
