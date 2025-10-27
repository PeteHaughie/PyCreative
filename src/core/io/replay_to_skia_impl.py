"""Minimal defensive replayer implementation used by the GPU presenter.

This module provides a small, robust `replay_to_skia_canvas` function
that implements the subset of ops used by examples: transforms,
background, line, rect and blend_mode. It's intentionally minimal to
avoid complex dependencies and to be safe to import at runtime.
"""

from __future__ import annotations

import math
import os
import logging
from typing import Sequence, Mapping, Any

try:
    import skia
except Exception:
    skia = None

try:
    from core.shape.stroke_utils import map_stroke_cap, map_stroke_join
except Exception:
    # best-effort: if imports fail, the map helpers won't be available
    map_stroke_cap = None
    map_stroke_join = None

logger = logging.getLogger(__name__)


def map_blend_mode(skia_mod, name: str):
    """Map a (possibly vendor/alias) blend-mode name to a skia.BlendMode value.

    This is defensive: skia Python bindings vary across versions and not all
    enum members exist with the same names. We attempt a few likely names
    for each logical mode and return the first one that exists.
    """
    if not name or skia_mod is None:
        return None
    n = str(name).upper()
    # Mapping of canonical logical names to candidate attribute names on
    # skia_mod.BlendMode (order is important — prefer the newer/expected
    # identifiers first).
    candidates = {
        'ADD': ('kPlus', 'kAdd'),
        'ADDITIVE': ('kPlus', 'kAdd'),
        'SCREEN': ('kScreen',),
        'MULTIPLY': ('kMultiply',),
        # 'SRC_OVER' is the usual "over" compositing mode (source over dest)
        'SRC_OVER': ('kSrcOver', 'kSrcOverMode',),
        # REPLACE maps to Src (source replaces dest) when available.
        'REPLACE': ('kSrc', 'kSrcOver',),
    }

    # Known aliases that may come from older code or user input
    aliases = {
        'OVER': 'SRC_OVER',
        'SRCOVER': 'SRC_OVER',
        'SRC_OVER': 'SRC_OVER',
        'REPLACE': 'REPLACE',
    }

    # Normalize via aliases then look up candidates
    key = aliases.get(n, n)
    cand = candidates.get(key)
    if cand is None:
        return None

    try:
        bm_container = getattr(skia_mod, 'BlendMode', None) or getattr(skia_mod, 'Blend', None)
        if bm_container is None:
            return None
        for attr in cand:
            try:
                val = getattr(bm_container, attr, None)
                if val is not None:
                    return val
            except Exception:
                continue

            
    except Exception:
        return None
    return None


def _make_paint_from_color(col, fill=True, stroke_weight=1.0, alpha=None, stroke_cap=None, stroke_join=None):
    if skia is None:
        return None
    p = skia.Paint()
    p.setAntiAlias(True)
    p.setStyle(skia.Paint.kFill_Style if fill else skia.Paint.kStroke_Style)
    if not fill:
        try:
            p.setStrokeWidth(float(stroke_weight))
        except Exception:
            pass
        # Apply stroke cap/join if provided and mapping helpers are available
        try:
            if stroke_cap is not None and map_stroke_cap is not None:
                try:
                    cap_val = map_stroke_cap(skia, stroke_cap)
                    if cap_val is not None:
                        try:
                            p.setStrokeCap(cap_val)
                        except Exception:
                            # older skia bindings may use setStrokeCap with int
                            try:
                                p.setStrokeCap(int(cap_val))
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception:
            pass
        try:
            if stroke_join is not None and map_stroke_join is not None:
                try:
                    join_val = map_stroke_join(skia, stroke_join)
                    if join_val is not None:
                        try:
                            p.setStrokeJoin(join_val)
                        except Exception:
                            try:
                                p.setStrokeJoin(int(join_val))
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception:
            pass

    if col is None:
        return p

    # Determine alpha: prefer explicit `alpha` argument; if not provided and
    # the color tuple contains an alpha component, use that. Default to 1.0.
    a = 1.0
    if alpha is not None:
        try:
            a = float(alpha)
        except Exception:
            a = 1.0
    else:
        # If color tuple includes alpha as 4th element, use it
        try:
            if isinstance(col, (tuple, list)) and len(col) >= 4:
                a = float(col[3]) / 255.0
        except Exception:
            pass
    a = max(0.0, min(1.0, a))
    try:
        if isinstance(col, (tuple, list)):
            r, g, b = [float(v) / 255.0 for v in col[:3]]
            try:
                p.setColor(skia.Color4f(r, g, b, a))
            except Exception:
                # Fallback to integer ARGB (alpha in high byte)
                ival = ((int(a * 255) & 0xFF) << 24) | ((int(r * 255) & 0xFF) << 16) | ((int(g * 255) & 0xFF) << 8) | (int(b * 255) & 0xFF)
                p.setColor(ival)
        else:
            v = float(col) / 255.0
            try:
                p.setColor(skia.Color4f(v, v, v, a))
            except Exception:
                ival = ((int(a * 255) & 0xFF) << 24) | ((int(v * 255) & 0xFF) << 16) | ((int(v * 255) & 0xFF) << 8) | (int(v * 255) & 0xFF)
                p.setColor(ival)
    except Exception:
        pass

    return p


def replay_to_skia_canvas(commands: Sequence[Mapping[str, Any]], canvas) -> None:
    """Replay a small set of drawing commands onto `canvas`.

    The goal is to be robust during present: no exceptions should
    propagate out of this function. Enable lifecycle debugging by
    setting PYCREATIVE_DEBUG_LIFECYCLE=1.
    """

    dbg = os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1'
    if skia is None:
        if dbg:
            logger.debug('replay_to_skia_impl: skia not available, skipping replay')
        return

    if dbg:
        try:
            logger.debug('replay_to_skia_impl: entering replay with %d commands', len(commands))
        except Exception:
            pass

    current_blend_mode = None
    current_tint = None
    current_fill = None
    current_fill_alpha = None
    # Stroke state recorded by ops like 'stroke', 'stroke_weight', 'stroke_cap', 'stroke_join'
    current_stroke = None
    current_stroke_alpha = None
    current_stroke_weight = 1
    current_stroke_cap = None
    current_stroke_join = None

    try:
        canvas.save()
        if hasattr(canvas, 'setMatrix'):
            canvas.setMatrix(skia.Matrix())
    except Exception:
        pass

    for i, cmd in enumerate(commands):
        op = cmd.get('op')
        args = cmd.get('args', {}) or {}
        if dbg and i < 16:
            try:
                logger.debug('replay_to_skia_impl op=%s args=%s', op, args)
            except Exception:
                pass

        try:
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

            if op == 'translate':
                tx = float(args.get('x', 0))
                ty = float(args.get('y', 0))
                try:
                    canvas.translate(tx, ty)
                except Exception:
                    try:
                        m = skia.Matrix()
                        m.setTranslate(tx, ty)
                        canvas.concat(m)
                    except Exception:
                        pass
                continue

            if op == 'rotate':
                a = float(args.get('angle', 0))
                deg = math.degrees(a)
                try:
                    canvas.rotate(deg)
                except Exception:
                    try:
                        m = skia.Matrix()
                        m.setRotate(deg)
                        canvas.concat(m)
                    except Exception:
                        pass
                continue

            if op == 'background':
                r = int(args.get('r', 200))
                g = int(args.get('g', 200))
                b = int(args.get('b', 200))
                try:
                    p = skia.Paint()
                    p.setStyle(skia.Paint.kFill_Style)
                    p.setAntiAlias(False)
                    try:
                        p.setColor(skia.Color4f(r / 255.0, g / 255.0, b / 255.0, 1.0))
                        canvas.drawPaint(p)
                    except Exception:
                        ival = (0xFF << 24) | (r << 16) | (g << 8) | b
                        p.setColor(ival)
                        canvas.drawPaint(p)
                except Exception:
                    try:
                        canvas.clear((0xFF << 24) | (r << 16) | (g << 8) | b)
                    except Exception:
                        pass
                continue

            if op == 'stroke':
                col = args.get('color') or args.get('c') or args.get('stroke')
                try:
                    current_stroke = tuple(col) if col is not None else None
                except Exception:
                    current_stroke = col
                # optional alpha may be provided
                try:
                    current_stroke_alpha = args.get('stroke_alpha') if args.get('stroke_alpha') is not None else getattr(current_stroke, 'stroke_alpha', None)
                except Exception:
                    current_stroke_alpha = args.get('stroke_alpha', None)
                continue

            if op == 'stroke_weight':
                try:
                    current_stroke_weight = float(args.get('weight', args.get('w', current_stroke_weight)))
                except Exception:
                    try:
                        current_stroke_weight = float(args.get('weight', current_stroke_weight))
                    except Exception:
                        pass
                continue

            if op == 'stroke_cap':
                try:
                    current_stroke_cap = args.get('cap') or args.get('cap_name') or args.get('c')
                except Exception:
                    current_stroke_cap = args.get('cap', None)
                continue

            if op == 'stroke_join':
                try:
                    current_stroke_join = args.get('join') or args.get('j')
                except Exception:
                    current_stroke_join = args.get('join', None)
                continue

            if op == 'blend_mode':
                bm = args.get('mode') or args.get('m') or args.get('blend')
                if bm is not None:
                    try:
                        current_blend_mode = str(bm)
                    except Exception:
                        current_blend_mode = bm
                continue

            if op == 'tint':
                # Record the current tint color (may be RGBA tuple or single value)
                col = args.get('color') or args.get('c')
                try:
                    current_tint = tuple(col) if col is not None else None
                except Exception:
                    current_tint = col
                # We don't implement full premultiplied-color tinting here; the
                # presence of a tint will be honored by any image-draw path that
                # supports paint/color filters. For now just record it.
                continue

            if op == 'line':
                x1 = float(args.get('x1', 0))
                y1 = float(args.get('y1', 0))
                x2 = float(args.get('x2', 0))
                y2 = float(args.get('y2', 0))
                stroke = args.get('stroke') if args.get('stroke') is not None else current_stroke
                sw = float(args.get('stroke_weight') if args.get('stroke_weight') is not None else (current_stroke_weight or 1))
                p = _make_paint_from_color(
                    stroke,
                    fill=False,
                    stroke_weight=sw,
                    alpha=args.get('stroke_alpha', None),
                    stroke_cap=args.get('stroke_cap', None),
                    stroke_join=args.get('stroke_join', None),
                )
                if p is None:
                    continue
                try:
                    if current_blend_mode is not None:
                        bm = map_blend_mode(skia, current_blend_mode)
                        if bm is not None:
                            try:
                                p.setBlendMode(bm)
                            except Exception:
                                pass
                except Exception:
                    pass
                try:
                    canvas.drawLine(x1, y1, x2, y2, p)
                except Exception:
                    try:
                        p1 = skia.Point(float(x1), float(y1))
                        p2 = skia.Point(float(x2), float(y2))
                        canvas.drawLine(p1, p2, p)
                    except Exception:
                        pass
                continue

            if op == 'point':
                x = float(args.get('x', 0))
                y = float(args.get('y', 0))
                # Per API: `fill()` has no effect on point; only stroke should
                # influence point rendering. We therefore ignore any explicit
                # fill and only draw when a stroke is provided.
                stroke_col = args.get('stroke') if args.get('stroke') is not None else current_stroke
                sw = float(args.get('stroke_weight', 1) or 0)
                # If stroke_weight is zero or negative, the point should not render.
                if sw <= 0 or stroke_col is None:
                    # per API, do not render when no stroke or zero weight
                    continue

                # radius: scale with stroke weight; make at least 0.5 for visibility
                rad = max(0.5, sw)

                sp = _make_paint_from_color(
                    stroke_col,
                    fill=False,
                    stroke_weight=sw,
                    alpha=args.get('stroke_alpha', None),
                    stroke_cap=args.get('stroke_cap', None),
                    stroke_join=args.get('stroke_join', None),
                )
                if sp is not None:
                    try:
                        canvas.drawCircle(x, y, rad, sp)
                    except Exception:
                        try:
                            canvas.drawRect(x, y, x + 1, y + 1, sp)
                        except Exception:
                            pass
                # otherwise: do nothing (fill should not render points)
                continue

            if op == 'circle':
                x = float(args.get('x', 0))
                y = float(args.get('y', 0))
                r = float(args.get('r', 0))
                # determine fill and stroke
                fill_col = args.get('fill') if args.get('fill') is not None else None
                stroke_col = args.get('stroke') if args.get('stroke') is not None else None
                try:
                    if fill_col is None:
                        fill_col = current_fill
                except Exception:
                    fill_col = None
                sw = float(args.get('stroke_weight') if args.get('stroke_weight') is not None else (current_stroke_weight or 1))

                # draw fill first if present
                if fill_col is not None:
                    fp = _make_paint_from_color(fill_col, fill=True, alpha=args.get('fill_alpha', None))
                    if fp is not None:
                        try:
                            if current_blend_mode is not None:
                                bm = map_blend_mode(skia, current_blend_mode)
                                if bm is not None:
                                    try:
                                        fp.setBlendMode(bm)
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                        try:
                            canvas.drawCircle(x, y, r, fp)
                        except Exception:
                            try:
                                canvas.drawCircle(float(x), float(y), float(r), fp)
                            except Exception:
                                pass

                # then stroke if requested
                if stroke_col is not None:
                    sp = _make_paint_from_color(
                        stroke_col,
                        fill=False,
                        stroke_weight=sw,
                        alpha=args.get('stroke_alpha', None),
                        stroke_cap=args.get('stroke_cap', None),
                        stroke_join=args.get('stroke_join', None),
                    )
                    if sp is not None:
                        try:
                            if current_blend_mode is not None:
                                bm = map_blend_mode(skia, current_blend_mode)
                                if bm is not None:
                                    try:
                                        sp.setBlendMode(bm)
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                        try:
                            canvas.drawCircle(x, y, r, sp)
                        except Exception:
                            try:
                                canvas.drawCircle(float(x), float(y), float(r), sp)
                            except Exception:
                                pass
                continue

            if op == 'ellipse':
                x = float(args.get('x', 0))
                y = float(args.get('y', 0))
                w = float(args.get('w', 0))
                h = float(args.get('h', 0))
                fill_col = args.get('fill') if args.get('fill') is not None else None
                sw = float(args.get('stroke_weight') if args.get('stroke_weight') is not None else (current_stroke_weight or 1))
                stroke_col = args.get('stroke') if args.get('stroke') is not None else current_stroke
                try:
                    if fill_col is None:
                        fill_col = current_fill
                except Exception:
                    fill_col = None

                # draw fill
                if fill_col is not None:
                    fp = _make_paint_from_color(fill_col, fill=True, alpha=args.get('fill_alpha', None))
                    if fp is not None:
                        try:
                            if current_blend_mode is not None:
                                bm = map_blend_mode(skia, current_blend_mode)
                                if bm is not None:
                                    try:
                                        fp.setBlendMode(bm)
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                        drew = False
                        try:
                            rect = skia.Rect.MakeXYWH(x, y, w, h)
                            canvas.drawOval(rect, fp)
                            drew = True
                        except Exception:
                            pass
                        if not drew:
                            try:
                                canvas.drawOval(x, y, x + w, y + h, fp)
                                drew = True
                            except Exception:
                                pass

                # draw stroke if present
                if stroke_col is not None:
                    scap = args.get('stroke_cap') if args.get('stroke_cap') is not None else current_stroke_cap
                    sjoin = args.get('stroke_join') if args.get('stroke_join') is not None else current_stroke_join
                    sp = _make_paint_from_color(
                        stroke_col,
                        fill=False,
                        stroke_weight=sw,
                        alpha=args.get('stroke_alpha', None),
                        stroke_cap=scap,
                        stroke_join=sjoin,
                    )
                    if sp is not None:
                        try:
                            if current_blend_mode is not None:
                                bm = map_blend_mode(skia, current_blend_mode)
                                if bm is not None:
                                    try:
                                        sp.setBlendMode(bm)
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                        try:
                            rect = skia.Rect.MakeXYWH(x, y, w, h)
                            canvas.drawOval(rect, sp)
                        except Exception:
                            try:
                                canvas.drawOval(x, y, x + w, y + h, sp)
                            except Exception:
                                pass
                continue

            if op == 'shape':
                mode = str(args.get('mode', 'POLYGON')).upper()
                verts = args.get('vertices') or []
                close = bool(args.get('close', False))
                # Determine a default fill/stroke for the whole shape if present
                fill_col = args.get('fill') if args.get('fill') is not None else None
                fill_alpha = args.get('fill_alpha', None)
                stroke_col = args.get('stroke') if args.get('stroke') is not None else None
                stroke_alpha = args.get('stroke_alpha', None)
                # use recorded stroke/fill state as fallbacks when not provided
                if fill_col is None:
                    fill_col = current_fill
                    if fill_alpha is None:
                        fill_alpha = current_fill_alpha
                if stroke_col is None:
                    stroke_col = current_stroke
                    if stroke_alpha is None:
                        stroke_alpha = current_stroke_alpha
                sw = float(args.get('stroke_weight') if args.get('stroke_weight') is not None else (current_stroke_weight or 1))

                try:
                    # Helper to extract per-vertex color if present
                    def _vertex_color(v):
                        try:
                            return v[2] if len(v) >= 3 else None
                        except Exception:
                            return None

                    def _vertex_alpha(v):
                        try:
                            return v[3] if len(v) >= 4 else None
                        except Exception:
                            return None

                    if mode == 'POINTS':
                        # Draw each vertex as a tiny point (respect per-vertex fill or global stroke)
                        for v in verts:
                            vx, vy = float(v[0]), float(v[1])
                            vfill = _vertex_color(v) or fill_col
                            valpha = _vertex_alpha(v) if _vertex_alpha(v) is not None else fill_alpha
                            if vfill is not None:
                                p = _make_paint_from_color(vfill, fill=True, alpha=valpha)
                                if p is not None:
                                    try:
                                        canvas.drawCircle(vx, vy, 1.0, p)
                                    except Exception:
                                        pass
                            elif stroke_col is not None:
                                sp = _make_paint_from_color(
                                    stroke_col,
                                    fill=False,
                                    stroke_weight=sw,
                                    alpha=stroke_alpha,
                                    stroke_cap=args.get('stroke_cap', None),
                                    stroke_join=args.get('stroke_join', None),
                                )
                                if sp is not None:
                                    try:
                                        canvas.drawCircle(vx, vy, max(0.5, sw), sp)
                                    except Exception:
                                        pass
                        continue

                    if mode in ('POLYGON', 'LINES'):
                        # Build a single path from vertices
                        if len(verts) >= 1:
                            try:
                                path = skia.Path()
                                first = verts[0]
                                path.moveTo(float(first[0]), float(first[1]))
                                for v in verts[1:]:
                                    path.lineTo(float(v[0]), float(v[1]))
                                if close:
                                    path.close()
                            except Exception:
                                path = None

                            if path is not None:
                                # Fill if any vertex or global fill present
                                chosen_fill = fill_col
                                chosen_alpha = fill_alpha
                                if chosen_fill is None and len(verts) > 0:
                                    chosen_fill = _vertex_color(verts[0])
                                    chosen_alpha = _vertex_alpha(verts[0]) if _vertex_alpha(verts[0]) is not None else chosen_alpha

                                if chosen_fill is not None:
                                    fp = _make_paint_from_color(chosen_fill, fill=True, alpha=chosen_alpha)
                                    if fp is not None:
                                        try:
                                            canvas.drawPath(path, fp)
                                        except Exception:
                                            pass

                                if stroke_col is not None:
                                    scap = args.get('stroke_cap') if args.get('stroke_cap') is not None else current_stroke_cap
                                    sjoin = args.get('stroke_join') if args.get('stroke_join') is not None else current_stroke_join
                                    sp = _make_paint_from_color(
                                        stroke_col,
                                        fill=False,
                                        stroke_weight=sw,
                                        alpha=stroke_alpha,
                                        stroke_cap=scap,
                                        stroke_join=sjoin,
                                    )
                                    if sp is not None:
                                        try:
                                            canvas.drawPath(path, sp)
                                        except Exception:
                                            pass
                        continue

                    if mode == 'TRIANGLES':
                        # Each consecutive 3 vertices form a triangle
                        for i in range(0, len(verts) - 2, 3):
                            a = verts[i]
                            b = verts[i + 1]
                            c = verts[i + 2]
                            try:
                                pth = skia.Path()
                                pth.moveTo(float(a[0]), float(a[1]))
                                pth.lineTo(float(b[0]), float(b[1]))
                                pth.lineTo(float(c[0]), float(c[1]))
                                pth.close()
                            except Exception:
                                pth = None
                            if pth is None:
                                continue
                            tri_fill = fill_col if fill_col is not None else (_vertex_color(a) or _vertex_color(b) or _vertex_color(c))
                            tri_alpha = fill_alpha if fill_alpha is not None else (_vertex_alpha(a) or _vertex_alpha(b) or _vertex_alpha(c))
                            if tri_fill is not None:
                                fp = _make_paint_from_color(tri_fill, fill=True, alpha=tri_alpha)
                                if fp is not None:
                                    try:
                                        canvas.drawPath(pth, fp)
                                    except Exception:
                                        pass
                            if stroke_col is not None:
                                scap = args.get('stroke_cap') if args.get('stroke_cap') is not None else current_stroke_cap
                                sjoin = args.get('stroke_join') if args.get('stroke_join') is not None else current_stroke_join
                                sp = _make_paint_from_color(
                                    stroke_col,
                                    fill=False,
                                    stroke_weight=sw,
                                    alpha=stroke_alpha,
                                    stroke_cap=scap,
                                    stroke_join=sjoin,
                                )
                                if sp is not None:
                                    try:
                                        canvas.drawPath(pth, sp)
                                    except Exception:
                                        pass
                        continue
                except Exception:
                    # Keep presenter robust — skip shape if anything goes wrong
                    pass

            if op == 'fill':
                # Record a current fill color for subsequent shape ops.
                col = args.get('color') or args.get('fill') or args.get('c')
                try:
                    current_fill = tuple(col) if col is not None else None
                    current_fill_alpha = args.get('fill_alpha', None)
                except Exception:
                    current_fill = col
                continue

            if op == 'rect':
                x = float(args.get('x', 0))
                y = float(args.get('y', 0))
                w = float(args.get('w', 0))
                h = float(args.get('h', 0))
                # Prefer explicit fill/stroke on the rect args, fall back to recorded `fill()`
                fill_col = args.get('fill') if args.get('fill') is not None else args.get('color') if args.get('color') is not None else None
                stroke_col = args.get('stroke') if args.get('stroke') is not None else None
                if fill_col is None:
                    try:
                        fill_col = current_fill
                    except Exception:
                        fill_col = None
                sw = float(args.get('stroke_weight', 1) or 1)

                # draw fill first
                if fill_col is not None:
                    fp = _make_paint_from_color(fill_col, fill=True, alpha=args.get('fill_alpha', None))
                    if fp is not None:
                        try:
                            if current_blend_mode is not None:
                                bm = map_blend_mode(skia, current_blend_mode)
                                if bm is not None:
                                    try:
                                        fp.setBlendMode(bm)
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                        drew = False
                        try:
                            canvas.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fp)
                            drew = True
                        except Exception:
                            pass
                        if not drew:
                            try:
                                canvas.drawRect(x, y, x + w, y + h, fp)
                                drew = True
                            except Exception:
                                pass
                        if not drew:
                            try:
                                r = skia.Rect.MakeLTRB(x, y, x + w, y + h)
                                canvas.drawRect(r, fp)
                                drew = True
                            except Exception:
                                pass

                # then stroke if specified
                if stroke_col is not None:
                    scap = args.get('stroke_cap') if args.get('stroke_cap') is not None else current_stroke_cap
                    sjoin = args.get('stroke_join') if args.get('stroke_join') is not None else current_stroke_join
                    sp = _make_paint_from_color(
                        stroke_col,
                        fill=False,
                        stroke_weight=sw,
                        alpha=args.get('stroke_alpha', None),
                        stroke_cap=scap,
                        stroke_join=sjoin,
                    )
                    if sp is not None:
                        try:
                            if current_blend_mode is not None:
                                bm = map_blend_mode(skia, current_blend_mode)
                                if bm is not None:
                                    try:
                                        sp.setBlendMode(bm)
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                        try:
                            canvas.drawRect(skia.Rect.MakeXYWH(x, y, w, h), sp)
                        except Exception:
                            try:
                                canvas.drawRect(x, y, x + w, y + h, sp)
                            except Exception:
                                try:
                                    r2 = skia.Rect.MakeLTRB(x, y, x + w, y + h)
                                    canvas.drawRect(r2, sp)
                                except Exception:
                                    pass
                continue

            if op == 'image':
                # Draw an image-like object. We attempt a few strategies in
                # order of preference:
                #  1) If the image object exposes `to_skia()`, use it.
                #  2) If it exposes `to_pillow()` or `to_pillow`, convert via
                #     Pillow and then to a Skia image (via frombytes/Pixmap).
                #  3) If raw bytes were recorded (image_bytes + image_size),
                #     reconstruct via skia.Image.frombytes.
                img_obj = args.get('image')
                ix = float(args.get('x', 0))
                iy = float(args.get('y', 0))
                skimg = None
                try:
                    if img_obj is not None:
                        # Preferred path: PCImage.to_skia exists in the
                        # repository and will perform conversion correctly.
                        if hasattr(img_obj, 'to_skia'):
                            try:
                                skimg = img_obj.to_skia()
                            except Exception:
                                skimg = None
                        elif hasattr(img_obj, 'to_pillow'):
                            try:
                                pil = img_obj.to_pillow()
                                if pil is not None:
                                    if pil.mode != 'RGBA':
                                        pil = pil.convert('RGBA')
                                    raw = pil.tobytes()
                                    w, h = pil.size
                                    try:
                                        dims = skia.ISize(w, h)
                                        skimg = skia.Image.frombytes(raw, dims, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
                                    except Exception:
                                        try:
                                            info = skia.ImageInfo.Make(w, h, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
                                            row_bytes = w * 4
                                            pix = skia.Pixmap(info, raw, row_bytes)
                                            skimg = skia.Image.MakeFromRaster(pix, None)
                                        except Exception:
                                            skimg = None
                            except Exception:
                                skimg = None
                    else:
                        # Try raw bytes path
                        raw = args.get('image_bytes')
                        size = args.get('image_size')
                        mode = args.get('image_mode', 'RGBA')
                        if raw and size:
                            try:
                                w, h = size
                                if mode != 'RGBA':
                                    # Convert via Pillow to ensure RGBA layout
                                    try:
                                        from PIL import Image as PILImage
                                        img_p = PILImage.frombytes(mode, (w, h), raw)
                                        img_p = img_p.convert('RGBA')
                                        raw2 = img_p.tobytes()
                                        dims = skia.ISize(w, h)
                                        skimg = skia.Image.frombytes(raw2, dims, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
                                    except Exception:
                                        skimg = None
                                else:
                                    try:
                                        dims = skia.ISize(w, h)
                                        skimg = skia.Image.frombytes(raw, dims, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
                                    except Exception:
                                        skimg = None
                            except Exception:
                                skimg = None
                except Exception:
                    skimg = None

                # If we managed to make a Skia image, draw it. We don't yet
                # implement complex tinting/alpha composition here.
                if skimg is not None:
                    try:
                        # canvas.drawImage expects a skia.Image (or compatible)
                        canvas.drawImage(skimg, ix, iy)
                    except Exception:
                        try:
                            # older/patched skia bindings sometimes require Image.makeTextureImage
                            canvas.drawImage(skimg, ix, iy)
                        except Exception:
                            pass
                else:
                    # If we couldn't make a skia image, skip silently but
                    # log when debugging lifecycle so the missing image is
                    # easier to trace.
                    if dbg:
                        try:
                            logger.debug('replay_to_skia_impl: could not create skia image for image op; skipping')
                        except Exception:
                            pass
                continue

            # Unknown ops are skipped to keep the presenter robust
        except Exception:
            if dbg:
                try:
                    logger.exception('replay_to_skia_impl: error replaying op %r', op)
                except Exception:
                    pass
            continue

    try:
        canvas.restore()
    except Exception:
        pass



