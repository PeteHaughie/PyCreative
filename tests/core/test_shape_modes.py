from core.shape import begin_shape, vertex, end_shape
from core.engine.impl import Engine


def _record_shape(mode, verts):
    eng = Engine(sketch_module=None, headless=True)
    begin_shape(eng, mode)
    for x, y in verts:
        vertex(eng, x, y)
    end_shape(eng)
    # Return the last recorded op of interest
    shapes = [c for c in eng.graphics.commands if c.get('op') in ('shape', 'invalid_shape')]
    if shapes:
        return shapes[-1]
    return None


def test_points_mode_accepts_vertices():
    op = _record_shape('POINTS', [(1, 1), (2, 2)])
    assert op is not None
    assert op['op'] == 'shape'


def test_lines_mode_even_vertices_ok():
    op = _record_shape('LINES', [(0, 0), (1, 1), (2, 2), (3, 3)])
    assert op is not None
    assert op['op'] == 'shape'


def test_lines_mode_odd_vertices_invalid():
    op = _record_shape('LINES', [(0, 0), (1, 1), (2, 2)])
    assert op is not None
    assert op['op'] == 'invalid_shape'


def test_triangles_mode_multiple_of_three_ok():
    op = _record_shape('TRIANGLES', [(0, 0), (1, 0), (0, 1)])
    assert op is not None
    assert op['op'] == 'shape'


def test_triangles_mode_bad_count_invalid():
    op = _record_shape('TRIANGLES', [(0, 0), (1, 0)])
    assert op is not None
    assert op['op'] == 'invalid_shape'


def test_polygon_accepts_any_count():
    op = _record_shape('POLYGON', [(0, 0), (1, 0), (1, 1), (0, 1)])
    assert op is not None
    assert op['op'] == 'shape'
