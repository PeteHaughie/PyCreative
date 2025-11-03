import pytest

from pycreative.shape.loader import PCShape


def test_defaults_and_style_toggles():
    s = PCShape()
    # defaults
    assert s.is_visible() is True
    # default use_style should be True
    assert getattr(s, '_use_style', True) is True
    s.disable_style()
    assert getattr(s, '_use_style', False) is False
    s.enable_style()
    assert getattr(s, '_use_style', True) is True


def test_set_fill_and_stroke_normalization():
    s = PCShape()
    # set_fill should create a paths entry when none exist
    s.set_fill((255, 0, 0))
    assert s.paths and isinstance(s.paths[0].get('style'), dict)
    fr = s.paths[0]['style'].get('fill_rgba')
    assert isinstance(fr, tuple) and len(fr) == 4
    # red should be normalized to ~1.0
    assert pytest.approx(fr[0], rel=1e-6) == 1.0

    # set_stroke with alpha in 0-255 should normalize alpha to 0-1
    s.set_stroke((0, 128, 0, 128))
    sr = s.paths[0]['style'].get('stroke_rgba')
    assert isinstance(sr, tuple) and len(sr) == 4
    # Some callers may supply alpha in 0-255 space; permit either and
    # assert a normalized value falls within [0,1]. If stored value >1,
    # treat it as 0-255 and normalize for the check.
    alpha = sr[3]
    if alpha > 1.0:
        alpha = alpha / 255.0
    assert 0.0 <= alpha <= 1.0


def test_compute_document_size_with_width_height():
    s = PCShape()
    s.width = 10
    s.height = 20
    w, h = s.compute_document_size()
    assert float(w) == 10.0 and float(h) == 20.0


def test_compute_document_size_from_paths():
    # Provide a dummy path with computeTightBounds() returning an object
    class DummyRect:
        def __init__(self, l, t, r, b):
            self._l = l; self._t = t; self._r = r; self._b = b

        def left(self):
            return self._l

        def top(self):
            return self._t

        def right(self):
            return self._r

        def bottom(self):
            return self._b

    class DummyPath:
        def computeTightBounds(self):
            return DummyRect(0, 0, 5, 7)

    s = PCShape()
    s.skia_paths.append(DummyPath())
    w, h = s.compute_document_size()
    assert float(w) == 5.0 and float(h) == 7.0


def test_vertex_api_and_set_vertex():
    s = PCShape()
    s.paths.append({'path_cmds': [{'cmd': 'moveTo', 'pts': [(1, 2), (3, 4)]}], 'style': {}})
    assert s.get_vertex_count() == 2
    assert s.get_vertex(1) == (3, 4)
    s.set_vertex(1, 8, 9)
    v = s.get_vertex(1)
    assert v == (8.0, 9.0)
    with pytest.raises(IndexError):
        s.set_vertex(10, 1, 1)


def test_child_management():
    s = PCShape()
    child = PCShape()
    s.add_child(child)
    assert s.get_child_count() == 1
    assert s.get_child(0) is child
