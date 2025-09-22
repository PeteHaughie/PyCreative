"""
Unit tests for pycreative.graphics.Surface drawing helpers (mocked surface).
"""

from pycreative import Surface


class DummySurface:
    def __init__(self):
        self.calls = []

    def fill(self, color):
        self.calls.append(("fill", color))

    def blit(self, img, pos):
        self.calls.append(("blit", img, pos))

def test_rect_calls(monkeypatch):
    dummy = DummySurface()
    monkeypatch.setattr(
        "pygame.draw.rect",
        lambda surf, color, rect, width=0: surf.calls.append(
            ("rect", color, rect, width)
        ),
    )
    s = Surface(dummy)
    s.rect(1, 2, 3, 4, color=(5, 6, 7), width=2)
    assert dummy.calls == [("rect", (5, 6, 7), (1, 2, 3, 4), 2)]

def test_ellipse_calls(monkeypatch):
    dummy = DummySurface()
    monkeypatch.setattr(
        "pygame.draw.ellipse",
        lambda surf, color, rect, width=0: surf.calls.append(
            ("ellipse", color, rect, width)
        ),
    )
    s = Surface(dummy)
    s.ellipse(10, 20, 30, 40, color=(1, 2, 3), width=1)
    # x-w/2, y-h/2, w, h
    assert dummy.calls == [
        ("ellipse", (1, 2, 3), (10 - 30 / 2, 20 - 40 / 2, 30, 40), 1)
    ]

def test_line_calls(monkeypatch):
    dummy = DummySurface()
    monkeypatch.setattr(
        "pygame.draw.line",
        lambda surf, color, start, end, width=1: surf.calls.append(
            ("line", color, start, end, width)
        ),
    )
    s = Surface(dummy)
    s.line(1, 2, 3, 4, color=(9, 8, 7), width=5)
    assert dummy.calls == [("line", (9, 8, 7), (1, 2), (3, 4), 5)]

def test_triangle_calls(monkeypatch):
    dummy = DummySurface()
    monkeypatch.setattr(
        "pygame.draw.polygon",
        lambda surf, color, points, width=0: surf.calls.append(
            ("polygon", color, points, width)
        ),
    )
    s = Surface(dummy)
    s.triangle(1, 2, 3, 4, 5, 6, color=(9, 8, 7), width=5)
    assert dummy.calls == [("polygon", (9, 8, 7), [(1, 2), (3, 4), (5, 6)], 5)]

def test_quad_calls(monkeypatch):
    dummy = DummySurface()
    monkeypatch.setattr(
        "pygame.draw.polygon",
        lambda surf, color, points, width=0: surf.calls.append(
            ("polygon", color, points, width)
        ),
    )
    s = Surface(dummy)
    s.quad(1, 2, 3, 4, 5, 6, 7, 8, color=(9, 8, 7), width=5)
    assert dummy.calls == [("polygon", (9, 8, 7), [(1, 2), (3, 4), (5, 6), (7, 8)], 5)]

def test_arc_calls(monkeypatch):
    dummy = DummySurface()
    monkeypatch.setattr(
        "pygame.draw.arc",
        lambda surf, color, rect, start_angle, end_angle, width=1: surf.calls.append(
            ("arc", color, rect, start_angle, end_angle, width)
        ),
    )
    s = Surface(dummy)
    s.arc(10, 20, 30, 40, 0.1, 0.5, color=(1, 2, 3), width=2)
    assert dummy.calls == [
        ("arc", (1, 2, 3), (10 - 30 / 2, 20 - 40 / 2, 30, 40), 0.1, 0.5, 2)
    ]

def test_image_calls():
    dummy = DummySurface()
    img = object()
    s = Surface(dummy)
    s.image(img, 7, 8)
    assert dummy.calls == [("blit", img, (7, 8))]
