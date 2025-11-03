"""Skia-backed SVG loader adapter.

When `skia.SVGDOM` is available in the runtime, prefer it for high
fidelity SVG parsing and rendering. This module exposes the same
`load_svg` / `load_shape` API used by the other loaders but returns a
PCShape with an attached `_svg_dom` attribute that presenters can render
directly using Skia.
"""
from __future__ import annotations


from .loader import PCShape, _ensure_file


def load_svg(path: str) -> PCShape:
    """Load an SVG using skia.SVGDOM (when available) and wrap it in a PCShape.

    The returned PCShape will have a ``_svg_dom`` attribute containing the
    Skia DOM instance. Callers can still inspect ``skia_paths`` and ``paths``
    for compatibility, but drawing will typically be performed by calling
    ``dom.render(canvas)`` inside the Skia presenter.
    """
    _ensure_file(path)
    try:
        import skia
    except Exception as e:
        raise RuntimeError('skia is required for skia_svg_adapter') from e

    data = open(path, 'rb').read()
    # Create a skia stream from bytes and ask SVGDOM to parse it.
    try:
        stream = skia.MemoryStream(data)
    except Exception:
        # Fallback: try FILEStream path if MemoryStream unavailable
        try:
            stream = skia.FILEStream(path)
        except Exception as e:
            raise RuntimeError('failed to create skia stream for SVG') from e

    # Factory method name differs across bindings; use MakeFromStream when available
    dom = None
    try:
        if hasattr(skia.SVGDOM, 'MakeFromStream'):
            dom = skia.SVGDOM.MakeFromStream(stream)
        else:
            # try constructor-style factory
            dom = skia.SVGDOM(stream)
    except Exception:
        dom = None

    if dom is None:
        raise RuntimeError('skia.SVGDOM failed to parse SVG')

    shape = PCShape()
    # attach the DOM for presenters to use
    setattr(shape, '_svg_dom', dom)

    # try to pull a container/document size from the DOM
    try:
        size = dom.containerSize()
        w = h = None
        # size may be a pair or an object with width()/height()
        try:
            if isinstance(size, (tuple, list)) and len(size) >= 2:
                w = float(size[0])
                h = float(size[1])
            elif hasattr(size, 'width') and hasattr(size, 'height'):
                try:
                    w = float(size.width())
                    h = float(size.height())
                except Exception:
                    w = h = None
            else:
                # try sequence access as a final fallback
                try:
                    w = float(size[0])
                    h = float(size[1])
                except Exception:
                    w = h = None
        except Exception:
            w = h = None
        # If DOM returned a zero-size (common when SVG uses percentage
        # width/height), fallback to the viewBox size declared in the SVG
        # root element.
        try:
            if w is not None and h is not None and (w == 0.0 or h == 0.0):
                vb = None
                try:
                    import xml.etree.ElementTree as ET
                    txt = open(path, 'rb').read()
                    try:
                        root = ET.fromstring(txt.lstrip())
                    except Exception:
                        root = ET.fromstring(txt.decode('utf-8').lstrip())
                    vb = (root.get('viewBox') or root.get('viewbox') or '').strip()
                except Exception:
                    vb = None
                if vb:
                    parts = [p for p in __import__('re').split(r"[\s,]+", vb) if p]
                    if len(parts) >= 4:
                        try:
                            w = float(parts[2])
                            h = float(parts[3])
                        except Exception:
                            pass
        except Exception:
            pass
        if w is not None:
            shape.width = w
        if h is not None:
            shape.height = h
    except Exception:
        # best-effort only
        pass

    return shape


def load_shape(path: str) -> PCShape:
    return load_svg(path)


__all__ = ['load_svg', 'load_shape']
