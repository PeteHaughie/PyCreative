from src.api import drawing as d


def test_line_descriptor():
    assert d.line(0, 0, 10, 10) == {"type": "line", "x1": 0, "y1": 0, "x2": 10, "y2": 10}


def test_rect_descriptor():
    assert d.rect(1, 2, 3, 4) == {"type": "rect", "x": 1, "y": 2, "w": 3, "h": 4}


def test_circle_descriptor():
    assert d.circle(5, 5, 10) == {"type": "circle", "x": 5, "y": 5, "r": 10}


def test_polygon_descriptor():
    pts = [(0, 0), (1, 1), (2, 2)]
    assert d.polygon(pts) == {"type": "polygon", "points": pts}


def test_square_and_ellipse_descriptors():
    assert d.square(2, 3, 4) == {"type": "square", "x": 2, "y": 3, "s": 4}
    assert d.ellipse(0, 0, 10, 20) == {"type": "ellipse", "x": 0, "y": 0, "w": 10, "h": 20}


def test_triangle_quad_and_bezier_descriptors():
    assert d.triangle(0, 0, 1, 1, 2, 2) == {"type": "triangle", "points": [(0, 0), (1, 1), (2, 2)]}
    assert d.quad(0, 0, 1, 1, 2, 2, 3, 3) == {"type": "quad", "points": [(0, 0), (1, 1), (2, 2), (3, 3)]}
    assert d.bezier(0, 0, 1, 1, 2, 2, 3, 3)["type"] == "bezier"


def test_text_and_path_descriptors():
    assert d.text("hi", 10, 20) == {"type": "text", "text": "hi", "x": 10, "y": 20}
    assert d.polyline([(0, 0), (1, 1)]) == {"type": "polyline", "points": [(0, 0), (1, 1)]}


