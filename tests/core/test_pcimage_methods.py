import pytest
from core.image import PCImage, create_image, load_image
from PIL import Image
from io import BytesIO


def test_load_and_save_and_get_set(tmp_path):
    # create a pillow image and wrap
    pil = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    pil.putpixel((2, 3), (1, 2, 3, 255))
    pc = PCImage(pil)
    assert pc.width == 8 and pc.height == 8
    assert pc.get(2, 3) == (1, 2, 3, 255)
    pc.set(2, 3, (10, 11, 12, 255))
    assert pc.get(2, 3) == (10, 11, 12, 255)
    # save to temp and reload via Pillow directly
    out = tmp_path / 'out.png'
    pc.save(str(out))
    r = Image.open(str(out))
    assert r.size == (8, 8)


def test_create_image_and_copy_resize():
    img = create_image(10, 5)
    assert img.width == 10 and img.height == 5
    img.set(1, 1, (20, 30, 40, 255))
    cp = img.copy()
    assert cp.get(1, 1) == (20, 30, 40, 255)
    r = img.resize(5, 2)
    assert r.width == 5 and r.height == 2


def test_get_rect_and_set_rect():
    base = create_image(16, 16)
    # draw a 4x4 red block in a region
    for y in range(4, 8):
        for x in range(4, 8):
            base.set(x, y, (255, 0, 0, 255))
    region = base.get_rect(4, 4, 4, 4)
    assert region.width == 4 and region.height == 4
    dest = create_image(16, 16)
    dest.set_rect(0, 0, region)
    assert dest.get(0, 0)[0] == 255


def test_mask_and_filter():
    base = create_image(8, 8)
    for y in range(8):
        for x in range(8):
            base.set(x, y, (10, 20, 30, 255))
    mask = create_image(8, 8)
    # set mask alpha 0 except a 2x2 box
    for y in range(8):
        for x in range(8):
            a = 255 if 2 <= x < 4 and 2 <= y < 4 else 0
            mask.set(x, y, (0, 0, 0, a))
    base.mask(mask)
    # after mask, alpha at (3,3) should be 255, elsewhere 0
    assert base.get(3, 3)[3] == 255
    assert base.get(0, 0)[3] == 0
    # filter
    gray = base.filter('GRAY')
    assert gray is not None
    thr = base.filter('THRESHOLD')
    assert thr is not None


def test_blend_color_and_blend():
    c1 = (100, 10, 20, 255)
    c2 = (100, 100, 100, 255)
    pc = PCImage(None, width=4, height=4)
    add = pc.blend_color(c1, c2, mode='ADD')
    assert add[0] == min(200, 200)
    mul = pc.blend_color(c1, c2, mode='MULTIPLY')
    assert isinstance(mul[0], int)
    # create base and other and blend
    base = create_image(4, 4)
    other = create_image(2, 2)
    other.set(0, 0, (255, 0, 0, 255))
    base.blend(other, mode='ADD', dx=1, dy=1)
    assert base.get(1, 1)[0] > 0


def test_load_pixels_update_pixels():
    p = create_image(2, 2)
    assert p.load_pixels() is True
    assert p.update_pixels() is True


def test_to_pillow_and_to_skia_if_available():
    p = create_image(4, 4)
    pil = p.to_pillow()
    assert pil is not None
    try:
        import skia
    except Exception:
        skia = None
    if skia is not None:
        skimg = p.to_skia()
        assert skimg is not None
