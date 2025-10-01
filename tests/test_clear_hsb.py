def test_clear_respects_hsb_mode(monkeypatch):
    """Ensure Surface.clear interprets a 3-tuple as HSB when color_mode('HSB') is active."""
    # Run pygame in headless mode for CI
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    import pygame
    from pycreative.graphics import Surface
    from pycreative.color import Color

    pygame.init()
    try:
        surf = pygame.Surface((10, 10))
        g = Surface(surf)

        # Set HSB mode like Processing: hue in 0..360, s/v in 0..100
        g.color_mode('HSB', 360, 100, 100)

        # Choose a known HSB value: pure red at hue=0, full saturation/brightness
        h, s, v = (0, 100, 100)
        g.clear((h, s, v))

        # Convert HSB to expected RGB using the library helper for robust comparison
        expected = Color.from_hsb(float(h), float(s), float(v), max_value=360).to_tuple()

        # Check the top-left pixel matches expected RGB
        px = surf.get_at((0, 0))[:3]
        assert px == expected, f"clear HSB -> expected {expected}, got {px}"
    finally:
        pygame.quit()
