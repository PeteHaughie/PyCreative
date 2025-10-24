"""PCImage representation backed by Pillow.

This keeps a simple API: width, height, pixels, get(x,y), set(x,y), save(path)
"""
from __future__ import annotations

from typing import Tuple, Optional, Any, cast


class PCImage:
    def __init__(self, pil_image=None, width: int = 0, height: int = 0):
        # store a Pillow Image internally when available
        self._pil = pil_image
        if pil_image is not None:
            try:
                self.width, self.height = pil_image.size
            except Exception:
                self.width = int(width)
                self.height = int(height)
        # mark whether the PCImage has real image data (used by request_image)
        self._loaded = bool(pil_image is not None)
        # simple lock for concurrent setters
        # initialize lock with an explicit Optional[Any] annotation so mypy
        # doesn't infer a concrete Lock type and then complain about assigning
        # None in fallback paths.
        self._lock: Optional[Any] = None
        try:
            import threading

            self._lock = threading.Lock()
        except Exception:
            self._lock = None

        # if no pil image provided, initialize with provided dims
        if pil_image is None:
            self.width = int(width)
            self.height = int(height)
    # diagnostics: (removed in cleanup) kept minimal internal state

    @property
    def pixels(self):
        # Return raw pixel access object (Pillow Image.load result) when available
        if self._pil is None:
            return None
        try:
            return self._pil.load()
        except Exception:
            return None

    def get(self, x: int, y: int) -> Optional[Tuple[int, int, int, int]]:
        if self._pil is None:
            return None
        try:
            return tuple(self._pil.getpixel((int(x), int(y))))
        except Exception:
            return None

    # NOTE: a more general `set` implementation (accepting colors or images)
    # appears further below; the older single-purpose setter was removed to
    # avoid duplicate definitions and to provide a single robust implementation.

    def save(self, path: str):
        if self._pil is None:
            raise RuntimeError('no image data')
        self._pil.save(path)

    def to_pillow(self):
        return self._pil

    def load_pixels(self):
        """Ensure the internal pixels[] are loaded. For Pillow-backed images
        this is a no-op but provided for API compatibility with Processing.
        """
        # Pillow loads pixels lazily; calling load() ensures internal buffer exists
        if self._pil is None:
            return None
        try:
            self._pil.load()
            return True
        except Exception:
            return False

    def update_pixels(self):
        """In Processing, updatePixels() writes the pixels[] buffer back to the
        image. With Pillow we keep pixels in sync, so this is a no-op.
        """
        return True

    def resize(self, new_w: int, new_h: int):
        """Resize the image in-place to the given dimensions and return self.

        Processing semantics expect resize() to modify the image. For
        Pillow-backed images we perform a resize and replace the internal
        image buffer. If no internal image exists, create a blank RGBA image
        of the requested size.
        """
        PILImage: Optional[Any] = None
        try:
            from PIL import Image as PILImage
        except Exception:
            PILImage = None

        try:
            nw = int(new_w)
            nh = int(new_h)
        except Exception:
            return self

        # If one dimension is zero, Processing semantics: return a new image
        # resized proportionally (do not mutate the original). If both
        # dimensions are non-zero, resize in-place and return self.
        if (nw == 0 and nh == 0) or (nw is None and nh is None):
            return self

        # Helper to create a new resized PCImage from self
        def _make_resized(new_w_px, new_h_px):
            try:
                if self._pil is None:
                    if PILImage is not None:
                        return PCImage(PILImage.new('RGBA', (new_w_px, new_h_px), (0, 0, 0, 0)))
                    return PCImage(None, width=new_w_px, height=new_h_px)
                pil2 = self._pil.resize((int(new_w_px), int(new_h_px)), resample=1)
                return PCImage(pil2)
            except Exception:
                return PCImage(None, width=new_w_px, height=new_h_px)

        # proportional branch: compute missing dimension
        if nw == 0 or nh == 0:
            # compute aspect from existing width/height; guard zero dims
            try:
                ow = float(getattr(self, 'width', 0) or (self._pil.size[0] if self._pil is not None else 0))
                oh = float(getattr(self, 'height', 0) or (self._pil.size[1] if self._pil is not None else 0))
                if ow == 0 or oh == 0:
                    # Nothing to scale from; return a blank/new image
                    if nw == 0 and nh > 0:
                        return _make_resized(max(1, int(oh)), nh)
                    if nh == 0 and nw > 0:
                        return _make_resized(nw, max(1, int(ow)))
                    return self
                if nw == 0 and nh > 0:
                    # scale width to preserve aspect
                    nw_calc = max(1, int(round((ow / oh) * float(nh))))
                    return _make_resized(nw_calc, nh)
                if nh == 0 and nw > 0:
                    nh_calc = max(1, int(round((oh / ow) * float(nw))))
                    return _make_resized(nw, nh_calc)
            except Exception:
                return self

        # Both non-zero: perform in-place resize (mutate) and return self
        try:
            pil2 = self._pil.resize((nw, nh), resample=1) if self._pil is not None else None
            if pil2 is not None:
                self._pil = pil2
                try:
                    self.width, self.height = pil2.size
                except Exception:
                    self.width, self.height = nw, nh
            else:
                # create blank image if none existed
                if PILImage is not None:
                    self._pil = PILImage.new('RGBA', (nw, nh), (0, 0, 0, 0))
                self.width, self.height = nw, nh
            return self
        except Exception:
            try:
                self.width = nw
                self.height = nh
            except Exception:
                pass
            return self

    def get_rect(self, x: int, y: int, w: int, h: int):
        """Return a new PCImage containing the rectangle at (x,y,w,h)."""
        if self._pil is None:
            return None
        try:
            box = (int(x), int(y), int(x + w), int(y + h))
            region = self._pil.crop(box)
            return PCImage(region)
        except Exception:
            return None

    # single-pixel get is implemented above and returns (r,g,b,a)

    def set_rect(self, x: int, y: int, other: 'PCImage'):
        """Paste another PCImage at position (x,y)."""
        if self._pil is None or other is None:
            return
        try:
            other_pil = cast( Any, other.to_pillow() if hasattr(other, 'to_pillow') else other )
            self._pil.paste(other_pil, (int(x), int(y)), other_pil if getattr(other_pil, 'mode', '') == 'RGBA' else None)
        except Exception:
            pass

    def set(self, x: int, y: int, value):
        """Write a single pixel or paste an image at x,y. Accepts color tuples or PCImage."""
        # If value is an image, delegate to set_rect
        if hasattr(value, 'to_pillow') or hasattr(value, 'mode'):
            try:
                other = value if hasattr(value, 'to_pillow') else PCImage(value)
                return self.set_rect(int(x), int(y), other)
            except Exception:
                return
        # Otherwise assume a color tuple
        if self._pil is None:
            return
        try:
            # Ensure image is RGBA so we write consistent 4-tuples
            try:
                if getattr(self._pil, 'mode', None) != 'RGBA':
                    self._pil = self._pil.convert('RGBA')
            except Exception:
                pass

            # Prefer direct pixel access via load() which is faster and
            # more consistent across Pillow versions than putpixel.
            try:
                px = self._pil.load()
                px[int(x), int(y)] = tuple(value)
                # write succeeded
            except Exception:
                # Fallback to putpixel if load() fails for some image types
                try:
                    self._pil.putpixel((int(x), int(y)), tuple(value))
                    # fallback write succeeded
                except Exception:
                    return
        except Exception:
            return

    def set_bytes(self, x: int, y: int, w: int, h: int, raw: bytes, mode: str = 'RGBA'):
        """Fast bulk-write: paste raw pixel bytes into the image at (x,y).

        - raw should be tightly-packed bytes matching `mode` (default 'RGBA').
        - If the region equals the whole image, this replaces the internal
          Pillow buffer with a new Image created from these bytes (fast).
        - For sub-regions we create a temporary Pillow Image and paste it.

        This avoids per-pixel Python loops and is much faster for large
        per-frame updates (e.g., writing a whole noise field).
        """
        if self._pil is None:
            # create placeholder if missing
            try:
                from PIL import Image as PILImage
                self._pil = PILImage.new('RGBA', (max(1, int(w + x)), max(1, int(h + y))), (0, 0, 0, 0))
                self.width, self.height = self._pil.size
            except Exception:
                return

        try:
            from PIL import Image as PILImage
        except Exception:
            return

        try:
            ix = int(x)
            iy = int(y)
            iw = int(w)
            ih = int(h)
        except Exception:
            return

        # Quick whole-image replace path
        try:
            if ix == 0 and iy == 0 and iw == getattr(self, 'width', 0) and ih == getattr(self, 'height', 0):
                # Create image directly from bytes and replace internal buffer
                try:
                    new = PILImage.frombytes(mode, (iw, ih), raw)
                except Exception:
                    # frombytes may require a copy path
                    new = PILImage.frombuffer(mode, (iw, ih), raw)
                if new is not None:
                    self._pil = new.convert('RGBA') if new.mode != 'RGBA' else new
                    try:
                        self.width, self.height = self._pil.size
                    except Exception:
                        pass
                    return
        except Exception:
            # Fall through to region paste below
            pass

        # Region paste: create temp image and paste with alpha if present
        try:
            try:
                region = PILImage.frombytes(mode, (iw, ih), raw)
            except Exception:
                region = PILImage.frombuffer(mode, (iw, ih), raw)
            if region.mode != 'RGBA':
                region = region.convert('RGBA')
            # Paste using alpha channel as mask so transparent pixels behave
            # correctly when compositing.
            try:
                self._pil.paste(region, (ix, iy), region)
            except Exception:
                # Pillow variants sometimes dislike 3rd argument; try without mask
                self._pil.paste(region, (ix, iy))
        except Exception:
            return

    def set_from_array(self, arr) -> None:
        """Convenience: accept a 2D numpy-like array of luminance (0..255)
        and set the entire image to the corresponding grayscale RGBA image.

        This function is optional and will only use numpy if available; if
        numpy is not present but `arr` supports the buffer protocol and has
        bytes in the right layout, consider using `set_bytes` instead.
        """
        try:
            import numpy as _np
        except Exception:
            return

        try:
            a = _np.asarray(arr, dtype=_np.uint8)
            if a.ndim == 2:
                h, w = a.shape
                rgba = _np.empty((h, w, 4), dtype=_np.uint8)
                rgba[:, :, 0] = a
                rgba[:, :, 1] = a
                rgba[:, :, 2] = a
                rgba[:, :, 3] = 255
                self.set_bytes(0, 0, w, h, rgba.tobytes(), mode='RGBA')
                return
            if a.ndim == 3 and a.shape[2] in (3, 4):
                h, w, c = a.shape
                if c == 3:
                    rgba = _np.concatenate([a, _np.full((h, w, 1), 255, dtype=_np.uint8)], axis=2)
                    self.set_bytes(0, 0, w, h, rgba.tobytes(), mode='RGBA')
                    return
                if c == 4:
                    self.set_bytes(0, 0, w, h, a.tobytes(), mode='RGBA')
                    return
        except Exception:
            return

    def copy(self):
        """Return a deep copy of the image as a new PCImage."""
        if self._pil is None:
            return PCImage(None, width=getattr(self, 'width', 0), height=getattr(self, 'height', 0))
        try:
            return PCImage(self._pil.copy())
        except Exception:
            return PCImage(None, width=getattr(self, 'width', 0), height=getattr(self, 'height', 0))

    def mask(self, mask_img: 'PCImage'):
        """Apply mask_img's alpha as a mask onto this image (in-place).

        mask_img: PCImage with alpha channel used as mask.
        """
        if self._pil is None or mask_img is None:
            return
        try:
            mask_pil = cast(Any, mask_img.to_pillow() if hasattr(mask_img, 'to_pillow') else mask_img)
            if mask_pil.mode != 'L':
                # convert alpha channel to 'L' grayscale
                if 'A' in mask_pil.getbands():
                    mask = mask_pil.split()[-1]
                else:
                    mask = mask_pil.convert('L')
            else:
                mask = mask_pil
            self._pil.putalpha(mask)
            try:
                self.width, self.height = self._pil.size
            except Exception:
                pass
        except Exception:
            pass

    def filter(self, mode: str = 'GRAY'):
        """Apply a simple filter: 'GRAY' -> grayscale, 'THRESHOLD' -> b/w.

        Returns a new PCImage.
        """
        if self._pil is None:
            return None
        try:
            if mode.upper() == 'GRAY':
                out = self._pil.convert('L').convert('RGBA')
                return PCImage(out)
            if mode.upper() == 'THRESHOLD':
                g = self._pil.convert('L')
                bw = g.point(lambda p: 255 if p > 128 else 0)
                out = bw.convert('RGBA')
                return PCImage(out)
        except Exception:
            pass
        return None

    def blend_color(self, c1, c2, mode='ADD'):
        """Blend two colors (r,g,b,a) according to simple modes. Returns tuple."""
        try:
            r1, g1, b1, a1 = c1
            r2, g2, b2, a2 = c2
            if mode == 'ADD':
                return (min(255, int(r1 + r2)), min(255, int(g1 + g2)), min(255, int(b1 + b2)), min(255, int(a1 + a2)))
            if mode == 'MULTIPLY':
                return (int(r1 * r2 / 255), int(g1 * g2 / 255), int(b1 * b2 / 255), int(a1 * a2 / 255))
        except Exception:
            pass
        return c1

    def blend(self, other: 'PCImage', mode='ADD', dx=0, dy=0):
        """Blend `other` into this image at (dx,dy) using simple blend modes."""
        if self._pil is None or other is None:
            return
        try:
            other_pil = cast( Any, other.to_pillow() if hasattr(other, 'to_pillow') else other )
            # operate per-pixel for correctness (not optimized)
            ow, oh = other_pil.size
            for y in range(oh):
                for x in range(ow):
                    try:
                        src = other_pil.getpixel((x, y))
                        dst = self._pil.getpixel((dx + x, dy + y))
                        blended = self.blend_color(dst, src, mode=mode)
                        self._pil.putpixel((dx + x, dy + y), blended)
                    except Exception:
                        continue
        except Exception:
            pass

    def to_skia(self):
        """Convert the internal Pillow image to a skia.Image (lazy import).

        Raises ImportError if skia is not available.
        """
        if self._pil is None:
            return None
        try:
            import skia
        except Exception:
            raise

        # Ensure RGBA mode
        img = self._pil
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        w, h = img.size
        raw = img.tobytes()
        # Create SkImage from raw bytes (assumes RGBA_8888)
        try:
            # skia.Image.frombytes expects (buffer, skia.ISize, colorType, alphaType)
            dims = skia.ISize(w, h)
            skimg = skia.Image.frombytes(raw, dims, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
            return skimg
        except Exception:
            # fallback to creating via Pixmap -> Image
            try:
                info = skia.ImageInfo.Make(w, h, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType)
                row_bytes = w * 4
                pix = skia.Pixmap(info, raw, row_bytes)
                img = skia.Image.MakeFromRaster(pix, None)
                return img
            except Exception:
                raise

    def _set_pillow(self, pil_image):
        """Thread-safe setter used by request_image to populate the image."""
        if self._lock:
            with self._lock:
                self._pil = pil_image
                try:
                    self.width, self.height = pil_image.size
                except Exception:
                    pass
                self._loaded = True
        else:
            self._pil = pil_image
            try:
                self.width, self.height = pil_image.size
            except Exception:
                pass
            self._loaded = True

    @property
    def loaded(self) -> bool:
        return bool(getattr(self, '_loaded', False))
