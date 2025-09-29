import pygame

from pycreative.graphics import OffscreenSurface


def test_get_set_pixel_roundtrip():
    raw = pygame.Surface((4, 3))
    surf = OffscreenSurface(raw)

    surf.clear((0, 0, 0))
    surf.set_pixel(1, 1, (10, 20, 30))
    assert surf.get_pixel(1, 1)[:3] == (10, 20, 30)


def test_get_pixels_and_set_pixels_roundtrip():
    raw = pygame.Surface((5, 4))
    surf = OffscreenSurface(raw)
    surf.clear((5, 6, 7))

    arr = surf.get_pixels()
    # shape H,W,C
    if hasattr(arr, 'shape'):
        h, w, c = arr.shape
        assert (h, w) == (4, 5)
        assert c in (3, 4)
        # modify a pixel and write back
        arr[0, 0, 0] = 123
        surf.set_pixels(arr)
        assert surf.get_pixel(0, 0)[0] == 123
    else:
        # fallback: list-of-lists
        assert len(arr) == 4


def test_save_load_roundtrip(tmp_path):
    raw = pygame.Surface((6, 6))
    surf = OffscreenSurface(raw)
    surf.clear((12, 34, 56))
    p = tmp_path / "pix.png"
    surf.save(str(p))
    loaded = pygame.image.load(str(p))
    assert loaded.get_at((0, 0))[:3] == (12, 34, 56)
