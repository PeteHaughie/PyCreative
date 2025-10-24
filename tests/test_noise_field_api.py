import pytest
import numpy as np

from core.engine.impl import Engine
from core.random import ops as ops


def test_noise_field_registered_and_writes():
    # Create headless engine which registers APIs
    engine = Engine(headless=True)

    # API should expose noise_field
    fn = engine.api.get('noise_field')
    assert callable(fn), "noise_field should be registered on engine.api"

    # Compute a small field via API and direct call and compare
    w, h = 64, 48
    arr_api = fn(w, h, inc=0.02)
    arr_direct = ops.noise_field(engine, w, h, inc=0.02)
    assert arr_api is not None and arr_direct is not None
    # arrays should be equal
    assert np.array_equal(arr_api, arr_direct)

    # Create an image and write the field via set_from_array
    img = engine.api.get('create_image')(w, h)
    assert img is not None
    img.set_from_array(arr_api)

    pil = img.to_pillow()
    assert pil is not None

    # Convert arr to RGBA and compare raw bytes
    rgba = np.empty((h, w, 4), dtype=np.uint8)
    rgba[:, :, 0] = arr_api
    rgba[:, :, 1] = arr_api
    rgba[:, :, 2] = arr_api
    rgba[:, :, 3] = 255

    from PIL import Image

    expected = Image.fromarray(rgba, 'RGBA')
    assert pil.tobytes() == expected.tobytes()
