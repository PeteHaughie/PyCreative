import os
import tempfile

import pytest

try:
    import skia
except Exception:
    skia = None

from core.image import create_image
from core.io.replay_to_skia import replay_to_skia_canvas


@pytest.mark.skipif(skia is None, reason="skia not available")
def test_replay_image_draws_pixels_correctly():
    # Create a small image with a red 8x8 block at (8,8)
    img = create_image(32, 32)
    for y in range(32):
        for x in range(32):
            img.set(x, y, (0, 0, 0, 0))
    for y in range(8, 16):
        for x in range(8, 16):
            img.set(x, y, (255, 0, 0, 255))

    # Record commands: background + image draw at (10,10)
    commands = [
        {'op': 'background', 'args': {'r': 10, 'g': 20, 'b': 30}},
        {'op': 'image', 'args': {'image': img, 'x': 10, 'y': 10, 'w': 32, 'h': 32, 'mode': 'CORNER'}},
    ]

    w, h = 64, 64
    surface = skia.Surface(w, h)
    canvas = surface.getCanvas()
    replay_to_skia_canvas(commands, canvas)

    snapshot = surface.makeImageSnapshot()
    # Encode the snapshot to PNG bytes and read with Pillow — this avoids
    # platform-dependent channel ordering in raw Skia buffers.
    data = snapshot.encodeToData()
    assert data is not None
    from io import BytesIO
    try:
        from PIL import Image as PILImage
    except Exception:
        pytest.skip('Pillow not available')
    pil = PILImage.open(BytesIO(data.bytes()))
    pil = pil.convert('RGBA')
    r, g, b, a = pil.getpixel((18, 18))
    # The expected red square should produce a red-dominant pixel with alpha 255
    assert r > 200
    assert g < 50
    assert b < 50
    assert a > 200
