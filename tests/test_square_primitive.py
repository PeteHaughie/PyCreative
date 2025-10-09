import sys
import pathlib


# Make src/ available on sys.path so tests can import the editable package
_here = pathlib.Path(__file__).resolve()
_repo = _here.parents[1]
src = _repo / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))


def test_square_draw_headless(monkeypatch):
    # Initialize pygame in headless mode before importing it
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    import pygame
    from pycreative.graphics import Surface

    pygame.init()
    surf = pygame.Surface((100, 100))
    g = Surface(surf)

    # Clear to black
    g.clear((0, 0, 0))

    # Draw a centered white square at (50,50) with side 20
    g.rect_mode(Surface.MODE_CENTER)
    g.fill((255, 255, 255))
    g.square(50, 50, 20)

    # Pixel at center should be white
    assert surf.get_at((50, 50))[:3] == (255, 255, 255)

    pygame.quit()
