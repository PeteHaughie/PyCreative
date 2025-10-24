import os
from pathlib import Path

import pytest


def make_png(path: Path, size=(8, 6), color=(10, 20, 30, 255)):
    try:
        from PIL import Image
    except Exception:
        pytest.skip("Pillow not available")
    img = Image.new('RGBA', size, color)
    img.save(path)


def test_load_image_returns_pcimage(tmp_path):
    # Arrange: create a small PNG in a data directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    img_path = data_dir / "small.png"
    make_png(img_path)

    # Act / Assert: import the public shim and call load_image
    from core.image import load_image

    pcimg = load_image(str(img_path))

    # PCImage contract: should expose width/height and pixels
    assert hasattr(pcimg, 'width')
    assert hasattr(pcimg, 'height')
    assert getattr(pcimg, 'width') == 8
    assert getattr(pcimg, 'height') == 6
    assert hasattr(pcimg, 'pixels')


def test_create_image_and_pixel_ops():
    from core.image import create_image

    img = create_image(10, 5)
    assert img.width == 10
    assert img.height == 5

    # pixels should be accessible and mutable via get/set
    assert hasattr(img, 'get') and callable(img.get)
    assert hasattr(img, 'set') and callable(img.set)

    # set a pixel and read it back
    img.set(2, 3, (1, 2, 3, 255))
    assert img.get(2, 3) == (1, 2, 3, 255)


def test_load_image_invalid_returns_error_pcimage(tmp_path):
    bad = tmp_path / "not_an_image.txt"
    bad.write_text("this is not an image")

    from core.image import load_image

    pcimg = load_image(str(bad))
    # Per docs, on error width/height may be -1
    assert getattr(pcimg, 'width', None) in (-1, None)
    assert getattr(pcimg, 'height', None) in (-1, None)


def test_request_image_async(tmp_path):
    data_dir = tmp_path / "data_async"
    data_dir.mkdir()
    img_path = data_dir / "async.png"
    make_png(img_path)

    from core.image import request_image

    pcimg = request_image(str(img_path))
    # placeholder should have width 0 initially
    assert getattr(pcimg, 'width', None) == 0

    # wait for background loader to complete
    import time

    for _ in range(20):
        if getattr(pcimg, 'loaded', False):
            break
        time.sleep(0.05)

    assert getattr(pcimg, 'loaded', False) is True
    assert pcimg.width == 8
    assert pcimg.height == 6


def test_to_skia_if_available(tmp_path):
    try:
        import skia  # type: ignore
    except Exception:
        import pytest

        pytest.skip('skia not installed')

    data_dir = tmp_path / "data_skia"
    data_dir.mkdir()
    img_path = data_dir / "skia.png"
    make_png(img_path)

    from core.image import load_image

    pcimg = load_image(str(img_path))
    skimg = pcimg.to_skia()
    assert skimg is not None
