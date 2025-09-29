import sys
import pathlib


# Make src/ available on sys.path so tests can import the editable package
_here = pathlib.Path(__file__).resolve()
_repo = _here.parents[1]
src = _repo / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))


def test_rect_and_ellipse_draw_headless(monkeypatch):
    # Initialize pygame in headless mode before importing it
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    import pygame
    from pycreative.graphics import Surface

    pygame.init()
    surf = pygame.Surface((100, 100))
    g = Surface(surf)

    # Clear to black
    g.clear((0, 0, 0))

    # Draw a filled white rect at center
    g.rect_mode(Surface.MODE_CENTER)
    g.fill((255, 255, 255))
    g.rect(50, 50, 20, 20)

    # Some pixel in the center should be white now
    assert surf.get_at((50, 50))[:3] == (255, 255, 255)

    # Draw an ellipse with stroke
    g.fill(None)
    g.stroke((255, 0, 0))
    g.stroke_weight(1)
    g.ellipse_mode(Surface.MODE_CENTER)
    g.ellipse(70, 70, 10, 10)

    # The border pixels should include red (stroke). Check several nearby points.
    stroke_color = (255, 0, 0)
    candidates = [(75, 70), (65, 70), (70, 75), (70, 65), (72, 74), (68, 66)]
    found = any(surf.get_at(p)[:3] == stroke_color for p in candidates)
    assert found, f"Expected stroke color {stroke_color} at one of {candidates}, got {[surf.get_at(p)[:3] for p in candidates]}"

    pygame.quit()
