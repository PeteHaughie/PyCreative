import pygame

from pycreative.graphics import Surface


def make_surface(w, h):
    surf = pygame.Surface((w, h), flags=pygame.SRCALPHA)
    return Surface(surf)


def test_image_corners_draws_in_expected_box():
    pygame.init()
    try:
        # Create a 10x10 destination surface
        dst = make_surface(10, 10)
        # Create a 4x2 source image with a distinct color
        src_surf = pygame.Surface((4, 2), flags=pygame.SRCALPHA)
        src_surf.fill((10, 20, 30, 255))
        # Set image mode to CORNERS so the call below treats (1,1,5,3) as corners
        dst.image_mode(dst.MODE_CORNERS)
        # Call image with x1,y1,x2,y2 — in our API this is image(img, x, y, w, h)
        # but when image_mode==CORNERS it should interpret w,h as x2,y2
        dst.image(src_surf, 1, 1, 5, 3)
        # After drawing, the pixels in box x=[1..4], y=[1..2] should be set to the source color
        for y in range(10):
            for x in range(10):
                px = dst.raw.get_at((x, y))
                if 1 <= x < 5 and 1 <= y < 3:
                    assert px[:3] == (10, 20, 30)
                else:
                    # untouched pixels are transparent black by default
                    assert px[3] == 0
    finally:
        pygame.quit()
