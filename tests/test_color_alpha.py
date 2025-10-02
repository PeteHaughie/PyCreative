from pycreative.color import Color


def test_fill_accepts_rgba_and_hsba(monkeypatch):
    """Ensure Surface.fill/clear accept 4-element tuples (alpha preserved) in both RGB and HSB modes."""
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    import pygame
    from pycreative.graphics import Surface
    from pycreative.color import Color

    pygame.init()
    try:
        surf = pygame.Surface((2, 2), flags=0, depth=32)
        g = Surface(surf)

        # RGB with alpha
        g.fill((10, 20, 30, 128))
        # top-left pixel should match (10,20,30) and have alpha 128 if surface supports alpha
        px = surf.get_at((0, 0))
        assert px[0] == 10 and px[1] == 20 and px[2] == 30

        # HSB with alpha: set HSB mode with processing-style ranges
        g.color_mode('HSB', 360, 100, 100)
        g.fill((0, 100, 100, 200))  # pure red, alpha=200
        px2 = surf.get_at((0, 0))
        # Convert expected via Color helper
        expected = Color.from_hsb(0, 100, 100, max_h=360, max_s=100, max_v=100)
        assert px2[0] == expected.r and px2[1] == expected.g and px2[2] == expected.b
    finally:
        pygame.quit()


def test_from_hsb_preserves_alpha():
    # HSB with explicit alpha should scale according to max values
    c = Color.from_hsb(0, 0, 0, a=128, max_h=255, max_s=255, max_v=255, max_a=255)
    assert c.to_rgba_tuple() == (0, 0, 0, 128)


def test_from_rgb_preserves_alpha():
    c = Color.from_rgb(10, 20, 30, a=64, max_value=255)
    assert c.to_rgba_tuple() == (10, 20, 30, 64)
