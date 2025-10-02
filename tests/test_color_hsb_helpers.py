import pytest

from pycreative.color import Color


def test_to_hsb_primary_colors():
    # Red
    r = Color.from_rgb(255, 0, 0)
    h, s, v, a = r.to_hsb()
    assert h == 0
    assert s == 255
    assert v == 255

    # Green
    g = Color.from_rgb(0, 255, 0)
    h, s, v, a = g.to_hsb()
    # scaled to 0..255, green should be around 85 (255/3)
    assert abs(h - 85) <= 1
    assert s == 255
    assert v == 255

    # Blue
    b = Color.from_rgb(0, 0, 255)
    h, s, v, a = b.to_hsb()
    assert abs(h - 170) <= 1
    assert s == 255
    assert v == 255


def test_from_hsb_grayscale_preserves_value():
    # saturation 0 should produce grayscale where r==g==b == value
    c = Color.from_hsb(0, 0, 128, max_h=255, max_s=255, max_v=255)
    assert c.r == c.g == c.b
    assert c.r == pytest.approx(128, abs=1)
