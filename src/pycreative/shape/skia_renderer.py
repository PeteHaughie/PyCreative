from __future__ import annotations

from typing import Optional, Tuple
try:
    import skia
    _HAS_SKIA = True
except Exception:
    skia = None  # type: ignore
    _HAS_SKIA = False

from PIL import Image
from io import BytesIO
from collections import OrderedDict

# Simple LRU cache for rasters: key -> PIL.Image
# Keep a small cache to avoid re-rasterizing static shapes repeatedly.
_RASTER_CACHE_MAX = 128
_raster_cache = OrderedDict()


def _make_cache_key(shape, w: int, h: int):
    # Key composed of shape id, size and simple style/geometry fingerprint.
    return (
        id(shape),
        int(w) if w is not None else None,
        int(h) if h is not None else None,
        getattr(shape, 'fill', None),
        getattr(shape, 'stroke', None),
        getattr(shape, 'stroke_weight', None),
        getattr(shape, '_version', None),
        getattr(shape, 'stroke_linecap', None),
        getattr(shape, 'stroke_linejoin', None),
        getattr(shape, 'stroke_miterlimit', None),
        tuple(getattr(shape, 'stroke_dasharray', []) or []),
        getattr(shape, 'view_box', None),
        len(getattr(shape, 'subpaths', [])),
    )


def skia_rasterize_pshape_cached(shape, w: int, h: int) -> Optional[Image.Image]:
    """Cached wrapper around skia_rasterize_pshape. Returns a PIL.Image or None.

    Returns a copy of the cached image to avoid accidental mutation of cache contents.
    """
    key = _make_cache_key(shape, w, h)
    im = _raster_cache.get(key)
    if im is not None:
        # move to end (most-recently used)
        _raster_cache.move_to_end(key)
        try:
            return im.copy()
        except Exception:
            return im
    # produce raster
    im = skia_rasterize_pshape(shape, w, h)
    if im is not None:
        _raster_cache[key] = im.copy() if hasattr(im, 'copy') else im
        _raster_cache.move_to_end(key)
        # prune
        try:
            while len(_raster_cache) > _RASTER_CACHE_MAX:
                _raster_cache.popitem(last=False)
        except Exception:
            pass
    return im

def skia_rasterize_pshape(shape, w: int, h: int) -> Optional[Image.Image]:
    """Rasterize a PShape-like object into a PIL RGBA Image using Skia.

    This function is defensive: returns None when Skia unavailable or
    if rasterization fails.
    """
    if not _HAS_SKIA:
        print('skia_renderer: skia not available')
        return None
    try:
        # create surface
        info = skia.ImageInfo.Make(int(w), int(h), skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType)
        surf = skia.Surface.MakeRaster(info)
        if surf is None:
            print('skia_renderer: surface creation failed')
            return None
        canvas = surf.getCanvas()
        # clear transparent
        canvas.clear(skia.ColorTRANSPARENT)

        # compute viewBox mapping similar to PShape.draw
        map_scale_x = None
        if getattr(shape, 'view_box', None) is not None:
            vb_x, vb_y, vb_w, vb_h = shape.view_box
            if vb_w == 0:
                vb_w = 1.0
            if vb_h == 0:
                vb_h = 1.0
            sx = float(w) / float(vb_w)
            sy = float(h) / float(vb_h)
            scale = min(sx, sy)
            extra_x = float(w) - (vb_w * scale)
            extra_y = float(h) - (vb_h * scale)
            offset_x = (extra_x / 2.0) - (vb_x * scale)
            offset_y = (extra_y / 2.0) - (vb_y * scale)
            map_scale_x = scale
            map_scale_y = scale
            map_offset_x = offset_x
            map_offset_y = offset_y

        def _to_device(pt):
            x, y = pt
            if map_scale_x is not None:
                return (x * map_scale_x + map_offset_x, y * map_scale_y + map_offset_y)
            return (x, y)

        # draw skia paths if present
        paths = getattr(shape, '_skia_paths', None)
        if paths:
            for p in paths:
                try:
                    # transform path to target coords by applying a canvas transform
                    # if viewBox mapping was computed, apply matrix
                    if map_scale_x is not None:
                        m = skia.Matrix()
                        m.setScale(map_scale_x, map_scale_y)
                        m.postTranslate(map_offset_x, map_offset_y)
                        p = p.copy()
                        p.transform(m)
                    paint = skia.Paint()
                    paint.setAntiAlias(True)
                    # fill
                    col = getattr(shape, 'fill', None)
                    if col is not None:
                        try:
                            r, g, b = col
                            paint.setStyle(skia.Paint.kFill_Style)
                            paint.setColor(skia.ColorSetARGB(255, int(r), int(g), int(b)))
                            # fill-rule: evenodd vs nonzero
                            try:
                                fr = getattr(shape, 'fill_rule', None)
                                if fr is not None:
                                    if fr == 'evenodd' or fr == 'even-odd':
                                        ptype = skia.Path.FillType.kEvenOdd
                                    else:
                                        ptype = skia.Path.FillType.kWinding
                                    # set paint or path fill type when applicable
                                    try:
                                        p.setFillType(ptype)
                                    except Exception:
                                        try:
                                            paint.setFillType(ptype)
                                        except Exception:
                                            pass
                            except Exception:
                                pass
                            canvas.drawPath(p, paint)
                        except Exception:
                            pass
                    # stroke
                    scol = getattr(shape, 'stroke', None)
                    sw = getattr(shape, 'stroke_weight', None)
                    if scol is not None and sw:
                        try:
                            r, g, b = scol
                            sp = skia.Paint()
                            sp.setAntiAlias(True)
                            sp.setStyle(skia.Paint.kStroke_Style)
                            sp.setStrokeWidth(float(sw))
                            sp.setColor(skia.ColorSetARGB(255, int(r), int(g), int(b)))
                            # stroke-linecap
                            try:
                                lc = getattr(shape, 'stroke_linecap', None)
                                if lc is not None:
                                    if lc == 'round':
                                        sp.setStrokeCap(skia.Paint.kRound_Cap)
                                    elif lc == 'square':
                                        sp.setStrokeCap(skia.Paint.kSquare_Cap)
                                    else:
                                        sp.setStrokeCap(skia.Paint.kButt_Cap)
                            except Exception:
                                pass
                            # stroke-linejoin and miterlimit
                            try:
                                lj = getattr(shape, 'stroke_linejoin', None)
                                if lj is not None:
                                    if lj == 'round':
                                        sp.setStrokeJoin(skia.Paint.kRound_Join)
                                    elif lj == 'bevel':
                                        sp.setStrokeJoin(skia.Paint.kBevel_Join)
                                    else:
                                        sp.setStrokeJoin(skia.Paint.kMiter_Join)
                                mm = getattr(shape, 'stroke_miterlimit', None)
                                if mm is not None:
                                    sp.setStrokeMiter(float(mm))
                            except Exception:
                                pass
                            # dash array via PathEffect if available (use compatibility shim)
                            try:
                                dash = getattr(shape, 'stroke_dasharray', None)
                                if dash:
                                    try:
                                        from .skia_compat import make_dash
                                        pe = make_dash(dash, 0.0)
                                        if pe is not None:
                                            sp.setPathEffect(pe)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                            canvas.drawPath(p, sp)
                        except Exception:
                            pass
                except Exception as e:
                    print('skia_renderer: failed drawing path', e)
                    continue
        else:
            # Fall back to drawing flattened subpaths
            for sub in getattr(shape, 'subpaths', []):
                if not sub:
                    continue
                pth = skia.Path()
                x0, y0 = sub[0]
                x0d, y0d = _to_device((x0, y0))
                pth.moveTo(x0d, y0d)
                for px, py in sub[1:]:
                    dx, dy = _to_device((px, py))
                    pth.lineTo(dx, dy)
                # if closed
                if len(sub) >= 3 and sub[0] == sub[-1]:
                    pth.close()
                paint = skia.Paint()
                paint.setAntiAlias(True)
                col = getattr(shape, 'fill', None)
                if col is not None:
                    try:
                        r, g, b = col
                        paint.setStyle(skia.Paint.kFill_Style)
                        paint.setColor(skia.ColorSetARGB(255, int(r), int(g), int(b)))
                        canvas.drawPath(pth, paint)
                    except Exception:
                        pass
                scol = getattr(shape, 'stroke', None)
                sw = getattr(shape, 'stroke_weight', None)
                if scol is not None and sw:
                    try:
                        r, g, b = scol
                        sp = skia.Paint()
                        sp.setAntiAlias(True)
                        sp.setStyle(skia.Paint.kStroke_Style)
                        sp.setStrokeWidth(float(sw))
                        sp.setColor(skia.ColorSetARGB(255, int(r), int(g), int(b)))
                        canvas.drawPath(pth, sp)
                    except Exception:
                        pass

        img = surf.makeImageSnapshot()
        # Try encodeToData and several Data-like APIs (varies by skia build)
        try:
            data = img.encodeToData()
            if data is not None:
                # try common names
                for name in ('toBytes', 'to_bytes', 'bytes', 'asBytes'):
                    fn = getattr(data, name, None)
                    if fn:
                        try:
                            raw = fn() if callable(fn) else fn
                            try:
                                b = bytes(raw)
                            except Exception:
                                b = raw
                            im = Image.open(BytesIO(b)).convert('RGBA')
                            return im
                        except Exception:
                            continue
                # try bytes(data)
                try:
                    b = bytes(data)
                    im = Image.open(BytesIO(b)).convert('RGBA')
                    return im
                except Exception:
                    pass
        except Exception:
            pass

        # Fallback: try to read pixels from the surface directly (surf available)
        try:
            # surf.readPixels expects a buffer length of w*h*4
            buf = bytearray(int(w) * int(h) * 4)
            ok = surf.readPixels(info, buf)
            if ok:
                try:
                    im = Image.frombuffer('RGBA', (int(w), int(h)), bytes(buf), 'raw', 'RGBA', 0, 1).convert('RGBA')
                    return im
                except Exception:
                    pass
        except Exception:
            pass

        return None
    except Exception:
        import traceback
        traceback.print_exc()
        return None
