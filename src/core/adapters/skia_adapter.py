"""Adapter module for skia.

All direct imports of the `skia` library should live here. Other modules should
depend on this adapter rather than importing `skia` directly.
"""
try:
    import skia  # type: ignore
except Exception as exc:  # pragma: no cover - adapter will be patched in tests
    skia = None  # type: ignore
from src.core.debug import debug


def MakeSurface(info: dict):
    if skia is None:
        raise ImportError("skia is not available")
    # Real implementation would translate info into Skia image info and create surface
    # For now, call a MakeSurface-like factory if available on the skia import
    if hasattr(skia, "MakeSurface"):
        return skia.MakeSurface(info)
    # Fallback: return a simple dict to represent a surface
    return {"surface": True, **info}


def present(skia_surface, target_display_surface=None):
    """Present the skia surface to the given display surface.

    The exact mechanism depends on skia-python and pygame; this is a small
    helper that, when skia is available, attempts to flush the skia surface
    pixels into the target display surface. When skia is not available this
    is a no-op.
    """
    if skia is None:
        return None

    debug(f"skia_adapter.present called; target_display_surface={type(target_display_surface)}")

    # Attempt a fast raw-pixel path: snapshot the surface and read pixels
    # directly into a numpy array, then create a pygame surface using
    # pygame.image.frombuffer to avoid expensive encode/decode round-trips.
    try:
        img = None
        if hasattr(skia_surface, 'makeImageSnapshot'):
            img = skia_surface.makeImageSnapshot()
        elif hasattr(skia_surface, 'newImageSnapshot'):
            img = skia_surface.newImageSnapshot()

        if img is None:
            # Fallback: try a simple flush
            if hasattr(skia_surface, 'flush'):
                skia_surface.flush()
            return None

        w, h = img.width(), img.height()

        # Try numpy-based readPixels if available
        try:
            import numpy as _np  # type: ignore
        except Exception:
            _np = None

        raw_arr = None
        if _np is not None and hasattr(img, 'readPixels'):
            try:
                # Create an empty array and read into it. Skia expects a
                # contiguous buffer with rowBytes; use width*4 for RGBA8888.
                arr = _np.empty((h, w, 4), dtype=_np.uint8)
                row_bytes = arr.strides[0]
                # skia-python's readPixels signature may vary; try a couple
                # of common variants.
                try:
                    img.readPixels(arr, row_bytes)
                except Exception:
                    # Some bindings accept (imageInfo, buffer, rowBytes)
                    info = skia.ImageInfo.Make(w, h, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
                    img.readPixels(info, arr, row_bytes)
                raw_arr = arr
            except Exception:
                raw_arr = None

        if raw_arr is None:
            # Fallback: try toBytes/tobytes or encodeToData
            try:
                if hasattr(img, 'tobytes'):
                    b = img.tobytes()
                elif hasattr(img, 'toBytes'):
                    b = img.toBytes()
                else:
                    # last resort: encode to PNG and let pygame load it
                    data = img.encodeToData()
                    b = data.toBytes()
            except Exception:
                # If all else fails, flush and return
                if hasattr(skia_surface, 'flush'):
                    skia_surface.flush()
                return None

            # If we have raw bytes, create a pygame surface from buffer
            try:
                import pygame as _pg  # type: ignore
                surf = _pg.image.frombuffer(b, (w, h), 'RGBA')
                if target_display_surface is not None and hasattr(target_display_surface, 'blit'):
                    target_display_surface.blit(surf, (0, 0))
                    try:
                        _pg.display.flip()
                    except Exception:
                        pass
                return None
            except Exception:
                # Can't use pygame.frombuffer; return after flush
                if hasattr(skia_surface, 'flush'):
                    skia_surface.flush()
                return None

        # raw_arr present: handle premultiplied alpha if necessary
        try:
            # If the image is premultiplied, convert to straight alpha.
            # Many Skia surfaces are premultiplied; detect via skia AlphaType if possible.
            premul = False
            try:
                premul = (img.alphaType() == skia.AlphaType.kPremul_AlphaType)
            except Exception:
                premul = False

            arr = raw_arr
            if premul:
                # Vectorized un-premultiply
                a = arr[..., 3].astype(_np.float32) / 255.0
                mask = a > 0
                # Prevent division warnings; operate in float then cast back
                rgb = arr[..., :3].astype(_np.float32)
                rgb[mask] = (rgb[mask] / a[mask, None]).clip(0, 255)
                arr[..., :3] = rgb.astype(_np.uint8)

            # Create pygame surface from buffer; frombuffer expects a bytes object
            try:
                import pygame as _pg  # type: ignore
                buf = arr.tobytes()
                surf = _pg.image.frombuffer(buf, (w, h), 'RGBA')
                if target_display_surface is not None and hasattr(target_display_surface, 'blit'):
                    target_display_surface.blit(surf, (0, 0))
                    try:
                        _pg.display.flip()
                    except Exception:
                        pass
                return None
            except Exception:
                # Can't create pygame surface; fall back to flush
                if hasattr(skia_surface, 'flush'):
                    skia_surface.flush()
                return None

        except Exception:
            if hasattr(skia_surface, 'flush'):
                skia_surface.flush()
            return None

    except Exception:
        # As a last resort, try to flush the surface so any backends complete.
        try:
            if hasattr(skia_surface, 'flush'):
                skia_surface.flush()
        except Exception:
            pass
        return None
