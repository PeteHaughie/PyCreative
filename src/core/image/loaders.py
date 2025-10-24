"""Image loading helpers using Pillow.

Implements blocking `load_image()` and `create_image()` helpers. Async
`request_image()` can be added later.
"""
from __future__ import annotations

from typing import Optional, Any, cast

from .pcimage import PCImage
import concurrent.futures

# Simple shared executor for async loads
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def _make_error_image():
    # Per docs, return a PCImage with width/height = -1 to indicate error
    return PCImage(None, width=-1, height=-1)


def load_image(path: str, extension: Optional[str] = None) -> PCImage:
    try:
        from PIL import Image
    except Exception:
        # Pillow not available: return error PCImage
        return _make_error_image()

    try:
        # Pillow understands URLs only when built with requests handlers; for
        # our minimal implementation, let PIL open the path or raise.
        img = Image.open(path)
        # ensure consistent mode
        if getattr(img, 'mode', None) != 'RGBA':
            img = cast(Any, img.convert('RGBA'))
        return PCImage(img)
    except Exception:
        return _make_error_image()


def create_image(width: int, height: int, fmt: str = 'RGBA') -> PCImage:
    try:
        from PIL import Image
    except Exception:
        # Pillow missing: create a minimal empty PCImage
        return PCImage(None, width=width, height=height)

    try:
        img = Image.new(fmt, (int(width), int(height)), (0, 0, 0, 0))
        return PCImage(img)
    except Exception:
        return PCImage(None, width=width, height=height)


def request_image(path: str, extension: Optional[str] = None) -> PCImage:
    """Asynchronously load an image and populate a returned PCImage.

    Returns a PCImage immediately with width/height == 0 and populates it
    once loading completes. On error, width/height will be set to -1.
    """
    placeholder = PCImage(None, width=0, height=0)

    def _worker(p, target: PCImage):
        try:
            from PIL import Image
            img = Image.open(p)
            if img.mode != 'RGBA':
                img = cast(Any, img.convert('RGBA'))
            target._set_pillow(img)
        except Exception:
            # indicate error per docs
            target._set_pillow(None)
            target.width = -1
            target.height = -1

    # submit and return placeholder
    try:
        _EXECUTOR.submit(_worker, path, placeholder)
    except Exception:
        # if executor submission fails, try synchronous fallback
        _worker(path, placeholder)

    return placeholder
