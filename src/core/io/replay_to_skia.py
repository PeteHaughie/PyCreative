"""Replay recorded GraphicsBuffer commands onto a Skia Canvas.

This small helper mirrors the Pillow replayer but issues Skia draw calls
so the engine can render recorded commands into a Skia Surface (CPU or
GPU-backed) for presentation.
"""
# mypy: ignore-errors
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
            # Transform-related ops: save/restore/translate/rotate/scale/shear/reset/apply_matrix
            if op in ('push_matrix', 'save'):
                try:
                    canvas.save()
                except Exception:
                    pass
                continue
            if op in ('pop_matrix', 'restore'):
                try:
                    canvas.restore()
                except Exception:
                    pass
                continue
            if op == 'reset_matrix':
                try:
                    # Skia does not have a direct reset; restore to identity by
                    # saving, resetting CTM, and restoring stack appropriately.
                    # Simpler: set concat to identity via setMatrix if available.
                    if hasattr(canvas, 'setMatrix'):
                        canvas.setMatrix(skia.Matrix())
                    else:
                        # Fallback: save/restore to clear transforms
                        canvas.save()
                        canvas.restore()
                except Exception:
                    pass
                continue
            if op == 'translate':
                tx = float(args.get('x', 0))
                ty = float(args.get('y', 0))
                try:
                    canvas.translate(tx, ty)
                except Exception:
                    # Older/skia-python variants may require Matrix concat
                    try:
                        m = skia.Matrix()
                        m.setTranslate(tx, ty)
                        canvas.concat(m)
                    except Exception:
                        pass
                continue
            if op == 'rotate':
                a = float(args.get('angle', 0))
                try:
                    canvas.rotate(a)
                except Exception:
                    try:
                        m = skia.Matrix()
                        m.setRotate(a)
                        canvas.concat(m)
                    except Exception:
                        pass
                continue
            if op == 'scale':
                sx = float(args.get('sx', args.get('s', 1)))
                sy = float(args.get('sy', sx))
                try:
                    canvas.scale(sx, sy)
                except Exception:
                    try:
                        m = skia.Matrix()
                        m.setScale(sx, sy)
                        canvas.concat(m)
                    except Exception:
                        pass
                continue
            if op == 'shear_x':
                a = float(args.get('angle', 0))
                try:
                    # Skia Matrix has setSkew(kx, ky)
                    m = skia.Matrix()
                    m.setSkew(float(args.get('angle', 0)), 0.0)
                    canvas.concat(m)
                except Exception:
                    pass
                continue
            if op == 'shear_y':
                a = float(args.get('angle', 0))
                try:
                    m = skia.Matrix()
                    m.setSkew(0.0, float(args.get('angle', 0)))
                    canvas.concat(m)
                except Exception:
                    pass
                continue
            if op == 'apply_matrix':
                mat = args.get('matrix', None)
                vals = args.get('values', None)
                try:
                    if mat is not None:
                        # Accept either a sequence-like matrix (flat 3x3 or 4x4)
                        vals = list(mat)
                    if vals is not None:
                        if len(vals) == 9:
                            m = skia.Matrix()
                            # skia.Matrix.setAll accepts 9 vals in row-major
                            try:
                                m.setAll(*[float(v) for v in vals])
                                canvas.concat(m)
                            except Exception:
                                pass
                        elif len(vals) == 6:
                            # 6-element affine [a,b,c,d,e,f] -> setAll expects 9
                            a,b,c,d,e,f = [float(v) for v in vals]
                            m = skia.Matrix()
                            try:
                                m.setAll(a, b, c, d, e, f, 0.0, 0.0, 1.0)
                                canvas.concat(m)
                            except Exception:
                                pass
                        elif len(vals) == 16:
                            # 4x4 matrix: ignore for now (2D canvas); just skip
                            pass
                except Exception:
                    pass
                continue
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
            elif op == 'circle':
                x = float(args.get('x', 0))
                y = float(args.get('y', 0))
                r = float(args.get('r', 0))
                fill = args.get('fill')
                stroke = args.get('stroke')
                sw = float(args.get('stroke_weight', 1) or 1)
                # fill
                if fill is not None:
                    p = skia.Paint()
                    p.setAntiAlias(True)
                    p.setStyle(skia.Paint.kFill_Style)
                    if isinstance(fill, (tuple, list)):
                        rr, gg, bb = [float(v)/255.0 for v in fill[:3]]
                        try:
                            p.setColor(skia.Color4f(rr, gg, bb, 1.0))
                        except Exception:
                            p.setColor((int(rr*255)<<16)|(int(gg*255)<<8)|int(bb*255))
                    else:
                        v = float(fill)/255.0
                        try:
                            p.setColor(skia.Color4f(v, v, v, 1.0))
                        except Exception:
                            p.setColor(int(v*255))
                    try:
                        canvas.drawCircle(x, y, r/2.0, p)
                    except Exception:
                        try:
                            # fallback: drawOval using Rect
                            canvas.drawOval(skia.Rect.MakeLTRB(x - r/2.0, y - r/2.0, x + r/2.0, y + r/2.0), p)
                        except Exception:
                            pass
                # stroke
                if stroke is not None and sw > 0:
                    p = skia.Paint()
                    p.setStyle(skia.Paint.kStroke_Style)
                    p.setStrokeWidth(sw)
                    p.setAntiAlias(True)
                    if isinstance(stroke, (tuple, list)):
                        rr, gg, bb = [float(v)/255.0 for v in stroke[:3]]
                        try:
                            p.setColor(skia.Color4f(rr, gg, bb, 1.0))
                        except Exception:
                            p.setColor((int(rr*255)<<16)|(int(gg*255)<<8)|int(bb*255))
                    else:
                        v = float(stroke)/255.0
                        try:
                            p.setColor(skia.Color4f(v, v, v, 1.0))
                        except Exception:
                            p.setColor(int(v*255))
                    try:
                        canvas.drawCircle(x, y, r/2.0, p)
                    except Exception:
                        try:
                            canvas.drawOval(skia.Rect.MakeLTRB(x - r/2.0, y - r/2.0, x + r/2.0, y + r/2.0), p)
                        except Exception:
                            pass
            elif op == 'point':
                x = float(args.get('x', 0))
                y = float(args.get('y', 0))
                stroke = args.get('stroke')
                sw = float(args.get('stroke_weight', 1) or 1)
                # Prefer fill if available, otherwise use stroke. Represent
                # point as a tiny circle (radius = max(1, sw/2)).
                r = max(1.0, sw / 2.0)
                fill = args.get('fill')
                if fill is not None:
                    p = skia.Paint()
                    p.setAntiAlias(True)
                    p.setStyle(skia.Paint.kFill_Style)
                    if isinstance(fill, (tuple, list)):
                        rr, gg, bb = [float(v)/255.0 for v in fill[:3]]
                        try:
                            p.setColor(skia.Color4f(rr, gg, bb, 1.0))
                        except Exception:
                            p.setColor((int(rr*255)<<16)|(int(gg*255)<<8)|int(bb*255))
                    else:
                        v = float(fill)/255.0
                        try:
                            p.setColor(skia.Color4f(v, v, v, 1.0))
                        except Exception:
                            p.setColor(int(v*255))
                    try:
                        canvas.drawCircle(x, y, r, p)
                    except Exception:
                        pass
                elif stroke is not None and sw > 0:
                    p = skia.Paint()
                    p.setAntiAlias(True)
                    p.setStyle(skia.Paint.kStroke_Style)
                    p.setStrokeWidth(sw)
                    if isinstance(stroke, (tuple, list)):
                        rr, gg, bb = [float(v)/255.0 for v in stroke[:3]]
                        try:
                            p.setColor(skia.Color4f(rr, gg, bb, 1.0))
                        except Exception:
                            p.setColor((int(rr*255)<<16)|(int(gg*255)<<8)|int(bb*255))
                    else:
                        v = float(stroke)/255.0
                        try:
                            p.setColor(skia.Color4f(v, v, v, 1.0))
                        except Exception:
                            p.setColor(int(v*255))
                    try:
                        canvas.drawCircle(x, y, r, p)
                    except Exception:
                        pass
            elif op == 'ellipse':
                x = float(args.get('x', 0))
                y = float(args.get('y', 0))
                w = float(args.get('w', 0))
                h = float(args.get('h', w))
                fill = args.get('fill')
                stroke = args.get('stroke')
                sw = float(args.get('stroke_weight', 1) or 1)
                # draw filled ellipse
                if fill is not None:
                    p = skia.Paint()
                    p.setAntiAlias(True)
                    p.setStyle(skia.Paint.kFill_Style)
                    if isinstance(fill, (tuple, list)):
                        rr, gg, bb = [float(v)/255.0 for v in fill[:3]]
                        try:
                            p.setColor(skia.Color4f(rr, gg, bb, 1.0))
                        except Exception:
                            p.setColor((int(rr*255)<<16)|(int(gg*255)<<8)|int(bb*255))
                    else:
                        v = float(fill)/255.0
                        try:
                            p.setColor(skia.Color4f(v, v, v, 1.0))
                        except Exception:
                            p.setColor(int(v*255))
                    try:
                        canvas.drawOval(skia.Rect.MakeLTRB(x - w/2.0, y - h/2.0, x + w/2.0, y + h/2.0), p)
                    except Exception:
                        pass
                # draw stroked ellipse
                if stroke is not None and sw > 0:
                    p = skia.Paint()
                    p.setStyle(skia.Paint.kStroke_Style)
                    p.setStrokeWidth(sw)
                    p.setAntiAlias(True)
                    if isinstance(stroke, (tuple, list)):
                        rr, gg, bb = [float(v)/255.0 for v in stroke[:3]]
                        try:
                            p.setColor(skia.Color4f(rr, gg, bb, 1.0))
                        except Exception:
                            p.setColor((int(rr*255)<<16)|(int(gg*255)<<8)|int(bb*255))
                    else:
                        v = float(stroke)/255.0
                        try:
                            p.setColor(skia.Color4f(v, v, v, 1.0))
                        except Exception:
                            p.setColor(int(v*255))
                    try:
                        canvas.drawOval(skia.Rect.MakeLTRB(x - w/2.0, y - h/2.0, x + w/2.0, y + h/2.0), p)
                    except Exception:
                        pass
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
