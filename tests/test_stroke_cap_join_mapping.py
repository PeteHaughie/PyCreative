import skia
from core.shape.stroke_utils import map_stroke_cap, map_stroke_join


def test_map_stroke_cap_known_names():
    assert map_stroke_cap(skia, 'ROUND') == skia.Paint.kRound_Cap
    assert map_stroke_cap(skia, 'PROJECT') == skia.Paint.kSquare_Cap
    assert map_stroke_cap(skia, 'SQUARE') == skia.Paint.kButt_Cap


def test_map_stroke_join_known_names():
    assert map_stroke_join(skia, 'MITER') == skia.Paint.kMiter_Join
    assert map_stroke_join(skia, 'BEVEL') == skia.Paint.kBevel_Join
    assert map_stroke_join(skia, 'ROUND') == skia.Paint.kRound_Join
