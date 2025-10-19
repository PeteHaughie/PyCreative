"""Replay recorded GraphicsBuffer commands onto a Skia Canvas.

This small helper mirrors the Pillow replayer but issues Skia draw calls
so the engine can render recorded commands into a Skia Surface (CPU or
GPU-backed) for presentation.
"""
# mypy: ignore-errors
from __future__ import annotations

from typing import Any
import os


def replay_to_skia_canvas(commands: list, canvas: Any) -> None:
    try:
        import skia
    except Exception:
        raise
    dbg = os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1'
    # Maintain a simple drawing state so sequential ops like `fill()` and
    # `stroke()` affect later `shape` commands. This mirrors how sketches
    # set a current fill/stroke before emitting vertices.
    current_fill = None
    current_fill_alpha = None
    current_stroke = None
    current_stroke_alpha = None
    current_stroke_weight = 1.0

    def _make_paint_from_color(col, fill=True, stroke_weight=1.0, alpha=None):
        p = skia.Paint()
        p.setAntiAlias(True)
        if fill:
            p.setStyle(skia.Paint.kFill_Style)
        else:
            p.setStyle(skia.Paint.kStroke_Style)
            p.setStrokeWidth(float(stroke_weight))
        if col is None:
            return p
        try:
            # Normalize alpha to 0..1 if provided; default to 1.0
            a = 1.0
            if alpha is not None:
                try:
                    a = float(alpha)
                except Exception:
                    a = 1.0
            # clamp alpha
            if a < 0.0:
                a = 0.0
            if a > 1.0:
                a = 1.0
            if isinstance(col, (tuple, list)):
                r, g, b = [float(v)/255.0 for v in col[:3]]
                try:
                    p.setColor(skia.Color4f(r, g, b, a))
                except Exception:
                    # fallback to integer color (alpha not supported here)
                    p.setColor((int(r*255)<<16)|(int(g*255)<<8)|int(b*255))
            else:
                v = float(col)/255.0
                try:
                    p.setColor(skia.Color4f(v, v, v, a))
                except Exception:
                    p.setColor(int(v*255))
        except Exception:
            pass
        return p

    for cmd in commands:
        op = cmd.get('op')
        args = cmd.get('args', {})
        try:
            if dbg:
                try:
                    print(f"Lifecycle debug: replay_to_skia op={op} args={args}")
                except Exception:
                    pass
        except Exception:
            pass
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
                # Ensure we paint an opaque background. Some Skia bindings
                # vary in how canvas.clear handles alpha or Color4f; using
                # drawPaint with an explicit opaque Color4f guarantees we
                # get a fully-opaque background regardless of surface alpha
                # configuration.
                try:
                    p = skia.Paint()
                    p.setStyle(skia.Paint.kFill_Style)
                    p.setAntiAlias(False)
                    try:
                        p.setColor(skia.Color4f(r/255.0, g/255.0, b/255.0, 1.0))
                        canvas.drawPaint(p)
                    except Exception:
                        # Fallback to integer ARGB packed color
                        try:
                            ival = (0xFF << 24) | (r << 16) | (g << 8) | b
                            p.setColor(ival)
                            canvas.drawPaint(p)
                        except Exception:
                            # Last-resort: try canvas.clear as before
                            try:
                                canvas.clear(skia.Color4f(r/255.0, g/255.0, b/255.0, 1.0))
                            except Exception:
                                try:
                                    canvas.clear(ival)
                                except Exception:
                                    pass
                except Exception:
                    try:
                        canvas.clear((0xFF << 24) | (r << 16) | (g << 8) | b)
                    except Exception:
                        pass
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
            elif op == 'fill':
                # record current fill color for subsequent shape ops
                current_fill = args.get('color') or args.get('fill') or None
                # keep alpha information for later paint construction
                current_fill_alpha = args.get('fill_alpha', None)
                continue
            elif op == 'no_fill':
                current_fill = None
                continue
            elif op == 'stroke':
                current_stroke = args.get('color') or args.get('stroke') or None
                current_stroke_alpha = args.get('stroke_alpha', None)
                continue
            elif op == 'no_stroke':
                current_stroke = None
                continue
            elif op == 'stroke_weight':
                try:
                    current_stroke_weight = float(args.get('weight', args.get('w', 1)))
                except Exception:
                    current_stroke_weight = 1.0
                continue
            elif op == 'shape':
                verts = args.get('vertices', []) or []
                mode = str(args.get('mode', 'POLYGON')).upper()
                close = bool(args.get('close', False))
                # Build paints from current state, preserving any recorded alpha
                fill_p = _make_paint_from_color(current_fill, fill=True, alpha=current_fill_alpha)
                stroke_p = None
                if current_stroke is not None and current_stroke_weight > 0:
                    stroke_p = _make_paint_from_color(current_stroke, fill=False, stroke_weight=current_stroke_weight, alpha=current_stroke_alpha)

                # Helper: draw a triangle given three points
                def _draw_triangle(a, b, c):
                    try:
                        path = skia.Path()
                        path.moveTo(a[0], a[1])
                        path.lineTo(b[0], b[1])
                        path.lineTo(c[0], c[1])
                        path.close()
                        # prefer per-shape fill if provided in args
                        shape_fill = args.get('fill', None)
                        shape_alpha = args.get('fill_alpha', None)
                        if shape_fill is not None:
                            # build a paint from shape_fill and optional alpha
                            pf = _make_paint_from_color(shape_fill, fill=True, alpha=shape_alpha)
                            # draw triangle with per-shape paint
                            canvas.drawPath(path, pf)
                        elif current_fill is not None:
                            # draw triangle using current fill paint
                            canvas.drawPath(path, fill_p)
                        if stroke_p is not None:
                            canvas.drawPath(path, stroke_p)
                    except Exception:
                        pass

                # POLYGON: draw as a single closed path
                if mode == 'POLYGON':
                    try:
                        if len(verts) >= 2:
                            path = skia.Path()
                            path.moveTo(verts[0][0], verts[0][1])
                            for v in verts[1:]:
                                path.lineTo(v[0], v[1])
                            if close:
                                path.close()
                            if current_fill is not None:
                                canvas.drawPath(path, fill_p)
                            if stroke_p is not None:
                                canvas.drawPath(path, stroke_p)
                    except Exception:
                        pass
                elif mode == 'TRIANGLE_FAN':
                    # fan: verts[0] is center; triangles are (v0, vi, vi+1)
                    try:
                        if len(verts) >= 3:
                            v0 = verts[0]
                            for i in range(1, len(verts) - 1):
                                _draw_triangle(v0, verts[i], verts[i+1])
                    except Exception:
                        pass
                elif mode == 'TRIANGLES':
                    try:
                        for i in range(0, len(verts) - 2, 3):
                            _draw_triangle(verts[i], verts[i+1], verts[i+2])
                    except Exception:
                        pass
                elif mode == 'LINES':
                    try:
                        for i in range(0, len(verts) - 1, 2):
                            a = verts[i]
                            b = verts[i+1]
                            if stroke_p is not None:
                                canvas.drawLine(a[0], a[1], b[0], b[1], stroke_p)
                    except Exception:
                        pass
                elif mode == 'POINTS':
                    try:
                        for v in verts:
                            if current_fill is not None:
                                canvas.drawCircle(float(v[0]), float(v[1]), max(1.0, current_stroke_weight / 2.0), fill_p)
                            elif stroke_p is not None:
                                canvas.drawCircle(float(v[0]), float(v[1]), max(1.0, current_stroke_weight / 2.0), stroke_p)
                    except Exception:
                        pass
                continue
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
