"""Replay recorded GraphicsBuffer commands onto a Skia Canvas.

This small helper mirrors the Pillow replayer but issues Skia draw calls
so the engine can render recorded commands into a Skia Surface (CPU or
GPU-backed) for presentation.
"""
# mypy: ignore-errors
from __future__ import annotations

from typing import Any
import os
import logging


def replay_to_skia_canvas(commands: list, canvas: Any) -> None:
    try:
        import skia
    except Exception:
        raise
    dbg = os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1'
    logger = logging.getLogger(__name__)
    # Maintain a simple drawing state so sequential ops like `fill()` and
    # `stroke()` affect later `shape` commands. This mirrors how sketches
    # set a current fill/stroke before emitting vertices.
    current_fill = None
    current_fill_alpha = None
    current_stroke = None
    current_stroke_alpha = None
    current_stroke_weight = 1.0
    current_stroke_cap = None
    current_stroke_join = None
    current_tint = None

    def _make_paint_from_color(col, fill=True, stroke_weight=1.0, alpha=None, cap=None, join=None):
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
        # Apply stroke cap/join if requested (mapping to Skia enums)
        try:
            if (not fill) and cap is not None:
                try:
                    from core.shape.stroke_utils import map_stroke_cap
                    mc = map_stroke_cap(skia, cap)
                    if mc is not None:
                        p.setStrokeCap(mc)
                        if dbg:
                            try:
                                logger.debug("_make_paint_from_color applied stroke cap mapping: input=%s mapped=%s", cap, mc)
                            except Exception:
                                pass
                except Exception:
                    pass
            if (not fill) and join is not None:
                try:
                    from core.shape.stroke_utils import map_stroke_join
                    mj = map_stroke_join(skia, join)
                    if mj is not None:
                        p.setStrokeJoin(mj)
                        if dbg:
                            try:
                                logger.debug("_make_paint_from_color applied stroke join mapping: input=%s mapped=%s", join, mj)
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception:
            pass
        return p

    for cmd in commands:
        op = cmd.get('op')
        args = cmd.get('args', {})
        try:
            if dbg:
                try:
                    logger.debug("replay_to_skia op=%s args=%s", op, args)
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
                    eff_fill = fill
                    eff_fill_alpha = args.get('fill_alpha', None)
                    p = _make_paint_from_color(eff_fill, fill=True, alpha=eff_fill_alpha)
                    canvas.drawRect(skia.Rect.MakeLTRB(x, y, x + w, y + h), p)
                if stroke is not None and sw > 0:
                    eff_stroke = stroke
                    eff_stroke_alpha = args.get('stroke_alpha', None)
                    eff_cap = args.get('stroke_cap', None) or current_stroke_cap
                    eff_join = args.get('stroke_join', None) or current_stroke_join
                    p = _make_paint_from_color(eff_stroke, fill=False, stroke_weight=sw, alpha=eff_stroke_alpha, cap=eff_cap, join=eff_join)
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
                    eff_fill = fill
                    eff_fill_alpha = args.get('fill_alpha', None)
                    p = _make_paint_from_color(eff_fill, fill=True, alpha=eff_fill_alpha)
                    try:
                        canvas.drawCircle(x, y, r/2.0, p)
                    except Exception:
                        try:
                            canvas.drawOval(skia.Rect.MakeLTRB(x - r/2.0, y - r/2.0, x + r/2.0, y + r/2.0), p)
                        except Exception:
                            pass
                # stroke
                if stroke is not None and sw > 0:
                    eff_stroke = stroke
                    eff_stroke_alpha = args.get('stroke_alpha', None)
                    eff_cap = args.get('stroke_cap', None) or current_stroke_cap
                    eff_join = args.get('stroke_join', None) or current_stroke_join
                    p = _make_paint_from_color(eff_stroke, fill=False, stroke_weight=sw, alpha=eff_stroke_alpha, cap=eff_cap, join=eff_join)
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
                # Prefer stroke color/weight for points per API contract.
                # Fall back to current stroke or fill as necessary.
                stroke_arg = args.get('stroke', None)
                fill_arg = args.get('fill', None)
                sw = None
                try:
                    sw = float(args.get('stroke_weight', args.get('strokeWeight', None) or current_stroke_weight))
                except Exception:
                    sw = float(current_stroke_weight or 1.0)
                # radius derived from stroke weight
                r = max(1.0, sw / 2.0)

                # Determine effective stroke and fill colors
                eff_stroke = stroke_arg if stroke_arg is not None else current_stroke
                eff_fill = fill_arg if fill_arg is not None else current_fill

                # Only draw points when a stroke color exists. Do NOT fall back
                # to fill semantics for `point` — this matches the Processing
                # behavior expected by users: points are stroke-driven.
                if eff_stroke is not None:
                    eff_stroke_alpha = args.get('stroke_alpha', None) or current_stroke_alpha
                    eff_cap = args.get('stroke_cap', None) or current_stroke_cap
                    eff_join = args.get('stroke_join', None) or current_stroke_join
                    # Use stroke-style paint so stroke caps/join apply to points
                    p = _make_paint_from_color(eff_stroke, fill=False, stroke_weight=sw, alpha=eff_stroke_alpha, cap=eff_cap, join=eff_join)
                    try:
                        # If dbg, log the cap/join applied (the helper also logs, but inline paints
                        # which set cap/join directly may reach here in other branches.)
                        if dbg:
                            try:
                                from core.shape.stroke_utils import map_stroke_cap, map_stroke_join
                                mc = map_stroke_cap(skia, eff_cap)
                                mj = map_stroke_join(skia, eff_join)
                                logger.debug("point draw applying cap=%s mapped=%s join=%s mapped=%s stroke_w=%s", eff_cap, mc, eff_join, mj, sw)
                            except Exception:
                                pass
                        canvas.drawCircle(x, y, r, p)
                    except Exception:
                        pass
            elif op == 'fill':
                # record current fill color for subsequent shape ops
                current_fill = args.get('color') or args.get('fill') or None
                # keep alpha information for later paint construction
                current_fill_alpha = args.get('fill_alpha', None)
                continue
            elif op == 'tint':
                try:
                    current_tint = args.get('color') or args.get('c') or args.get('color')
                except Exception:
                    current_tint = None
                continue
            elif op == 'stroke_cap':
                # record the stroke cap for later paint construction
                try:
                    current_stroke_cap = args.get('cap')
                    if dbg:
                        try:
                            logger.debug("recorded stroke_cap op value=%s", current_stroke_cap)
                        except Exception:
                            pass
                except Exception:
                    current_stroke_cap = None
                continue
            elif op == 'stroke_join':
                try:
                    current_stroke_join = args.get('join')
                    if dbg:
                        try:
                            logger.debug("recorded stroke_join op value=%s", current_stroke_join)
                        except Exception:
                            pass
                except Exception:
                    current_stroke_join = None
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
                    # apply any recorded cap/join from args or current state
                    try:
                        eff_cap = args.get('stroke_cap', None) or current_stroke_cap
                        eff_join = args.get('stroke_join', None) or current_stroke_join
                        from core.shape.stroke_utils import map_stroke_cap, map_stroke_join
                        mc = map_stroke_cap(skia, eff_cap)
                        if dbg:
                            try:
                                logger.debug("ellipse mapping cap=%s -> %s", eff_cap, mc)
                            except Exception:
                                pass
                        if mc is not None:
                            p.setStrokeCap(mc)
                        mj = map_stroke_join(skia, eff_join)
                        if dbg:
                            try:
                                logger.debug("ellipse mapping join=%s -> %s", eff_join, mj)
                            except Exception:
                                pass
                        if mj is not None:
                            p.setStrokeJoin(mj)
                    except Exception:
                        pass
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
                # apply cap/join if present
                try:
                    from core.shape.stroke_utils import map_stroke_cap, map_stroke_join
                    eff_cap = args.get('stroke_cap', None) or current_stroke_cap
                    eff_join = args.get('stroke_join', None) or current_stroke_join
                    mc = map_stroke_cap(skia, eff_cap)
                    if dbg:
                        try:
                            logger.debug("line mapping cap=%s -> %s", eff_cap, mc)
                        except Exception:
                            pass
                    if mc is not None:
                        p.setStrokeCap(mc)
                    mj = map_stroke_join(skia, eff_join)
                    if dbg:
                        try:
                            logger.debug("line mapping join=%s -> %s", eff_join, mj)
                        except Exception:
                            pass
                    if mj is not None:
                        p.setStrokeJoin(mj)
                except Exception:
                    pass
                canvas.drawLine(x1, y1, x2, y2, p)
            elif op == 'image':
                # Draw an image-like object. The recorded args may include
                # a PCImage instance (which exposes to_skia()) or a raw
                # skia.Image. Support basic image_mode semantics: CORNER
                # (default) and CENTER. If width/height are provided, the
                # image will be scaled to that size.
                try:
                    img_obj = args.get('image') or args.get('img') or args.get('src')
                    if img_obj is None:
                        # some recorders may pass the first positional arg as 'a'
                        img_obj = args.get('a')
                    if img_obj is None:
                        continue

                    # Obtain a skia.Image from the object
                    skimg = None
                    # Prefer recorded raw bytes if present (snapshot at record time)
                    try:
                        img_bytes = args.get('image_bytes') if isinstance(args, dict) else None
                    except Exception:
                        img_bytes = None
                    if img_bytes is not None:
                        try:
                            # Reconstruct a skia.Image from raw RGBA bytes captured
                            w, h = args.get('image_size', (0, 0))
                            if w and h:
                                try:
                                    dims = skia.ISize(int(w), int(h))
                                    try:
                                        skimg = skia.Image.frombytes(img_bytes, dims, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
                                    except Exception:
                                        # fallback via Pixmap
                                        info = skia.ImageInfo.Make(int(w), int(h), skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
                                        row_bytes = int(w) * 4
                                        pm = skia.Pixmap(info, img_bytes, row_bytes)
                                        skimg = skia.Image.MakeFromRaster(pm, None)
                                except Exception:
                                    skimg = None
                        except Exception:
                            skimg = None
                    try:
                        if hasattr(img_obj, 'to_skia'):
                            skimg = img_obj.to_skia()
                        elif isinstance(img_obj, skia.Image):
                            skimg = img_obj
                        else:
                            # Try common conversions: pillow-like object
                            if hasattr(img_obj, 'to_pillow'):
                                pil = img_obj.to_pillow()
                                try:
                                    data = pil.tobytes()
                                    skimg = skia.Image.frombytes(pil.mode, skia.ISize(pil.size), data)
                                except Exception:
                                    try:
                                        # fallback: use Pixmap -> Image.MakeFromRaster
                                        w,h = pil.size
                                        row_bytes = w * len(pil.getbands())
                                        pm = skia.Pixmap(skia.ImageInfo.MakeN32Premul(w, h), pil.tobytes(), row_bytes)
                                        skimg = skia.Image.MakeFromRaster(pm, None)
                                    except Exception:
                                        skimg = None
                    except Exception:
                        skimg = None

                    if skimg is None:
                        # nothing we can draw
                        continue

                    # no-op: debug dump removed

                    # Destination rectangle calculation
                    mode = (args.get('mode') or args.get('image_mode') or 'CORNER').upper()
                    x = float(args.get('x', 0))
                    y = float(args.get('y', 0))
                    # support corners-style: (x1,y1,x2,y2)
                    if mode == 'CORNERS' or ('x2' in args and 'y2' in args):
                        try:
                            x2 = float(args.get('x2', args.get('x2', 0)))
                            y2 = float(args.get('y2', args.get('y2', 0)))
                            left = x
                            top = y
                            right = x2
                            bottom = y2
                        except Exception:
                            left = x
                            top = y
                            right = left + float(skimg.width())
                            bottom = top + float(skimg.height())
                    else:
                        # width/height (optional); default to image native size
                        try:
                            w = args.get('w', args.get('width', None))
                            h = args.get('h', args.get('height', None))
                            if w is None:
                                w = float(skimg.width())
                            else:
                                w = float(w)
                            if h is None:
                                h = float(skimg.height())
                            else:
                                h = float(h)
                        except Exception:
                            w = float(skimg.width())
                            h = float(skimg.height())

                        if mode == 'CENTER':
                            left = x - w/2.0
                            top = y - h/2.0
                        else:
                            # CORNER default
                            left = x
                            top = y
                        right = left + w
                        bottom = top + h

                    dest = skia.Rect.MakeLTRB(float(left), float(top), float(right), float(bottom))

                    # Attempt high-quality drawImageRect if available
                    try:
                        src = skia.Rect.MakeLTRB(0.0, 0.0, float(skimg.width()), float(skimg.height()))
                        paint = skia.Paint()
                        paint.setAntiAlias(True)
                        # Respect optional tint/alpha if provided (basic support)
                        tint = args.get('tint', None)
                        if tint is None:
                            tint = current_tint
                        alpha = args.get('alpha', None)
                        if alpha is not None:
                            try:
                                a = float(alpha)
                                a = max(0.0, min(1.0, a))
                                paint.setAlphaf(a)
                            except Exception:
                                pass
                        # Apply tint if provided. Try GPU ColorFilter first; fall back to CPU tinting via Pillow.
                        if tint is not None:
                            # Normalize tint to RGBA factors (0.0..1.0)
                            try:
                                if isinstance(tint, (tuple, list)):
                                    tr = float(tint[0]) / 255.0 if len(tint) > 0 else 1.0
                                    tg = float(tint[1]) / 255.0 if len(tint) > 1 else tr
                                    tb = float(tint[2]) / 255.0 if len(tint) > 2 else tr
                                    ta = float(tint[3]) / 255.0 if len(tint) > 3 else 1.0
                                else:
                                    # single numeric -> grayscale tint
                                    v = float(tint) / 255.0
                                    tr = tg = tb = v
                                    ta = 1.0
                            except Exception:
                                tr = tg = tb = 1.0
                                ta = 1.0
                            # Try to use Skia ColorFilter (matrix) to multiply channels
                            try:
                                # 4x5 color matrix: Rr,0,0,0,0, 0,g,0,0,0, 0,0,b,0,0, 0,0,0,a,0
                                mat = [
                                    tr, 0.0, 0.0, 0.0, 0.0,
                                    0.0, tg, 0.0, 0.0, 0.0,
                                    0.0, 0.0, tb, 0.0, 0.0,
                                    0.0, 0.0, 0.0, ta, 0.0,
                                ]
                                try:
                                    # Preferred API
                                    cf = skia.ColorFilter.MakeMatrix(mat)
                                except Exception:
                                    # Alternate API name
                                    cf = skia.ColorFilters.Matrix(mat)
                                paint.setColorFilter(cf)
                            except Exception:
                                # Fallback: CPU tint via Pillow
                                try:
                                    from PIL import Image, ImageChops
                                    pil = None
                                    if hasattr(img_obj, 'to_pillow'):
                                        pil = img_obj.to_pillow()
                                    else:
                                        # try to construct from skimg back to pillow via bytes
                                        # skia.Image -> bytes path can vary; attempt safe fallback
                                        pil = None
                                    if pil is not None:
                                        # Ensure RGBA
                                        p = pil.convert('RGBA')
                                        # Create solid color layer
                                        color_layer = Image.new('RGBA', p.size, (int(tr*255), int(tg*255), int(tb*255), int(ta*255)))
                                        try:
                                            tinted = ImageChops.multiply(p, color_layer)
                                        except Exception:
                                            # Simple blend as last-resort
                                            tinted = Image.blend(p, color_layer, 0.5)
                                        # Replace skimg with tinted version
                                        try:
                                            data = tinted.tobytes()
                                            dims = skia.ISize(tinted.size[0], tinted.size[1])
                                            skimg = skia.Image.frombytes(data, dims, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
                                        except Exception:
                                            try:
                                                w,h = tinted.size
                                                info = skia.ImageInfo.Make(w, h, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
                                                row_bytes = w * 4
                                                pix = skia.Pixmap(info, tinted.tobytes(), row_bytes)
                                                skimg = skia.Image.MakeFromRaster(pix, None)
                                            except Exception:
                                                pass
                                except Exception:
                                    pass
                        canvas.drawImageRect(skimg, src, dest, paint)
                    except Exception:
                        try:
                            # Fallback: draw at left/top unscaled
                            canvas.drawImage(skimg, float(left), float(top))
                        except Exception:
                            pass
                except Exception:
                    # Best-effort: do not fail the whole replay due to image draw
                    try:
                        if dbg:
                            logger.exception("failed to draw image op")
                    except Exception:
                        pass
                continue
        except Exception:
            # best-effort: ignore commands that fail to draw
            continue
