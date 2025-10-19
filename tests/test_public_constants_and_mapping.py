import skia
import pycreative
from core.shape.stroke_utils import map_stroke_cap, map_stroke_join


def test_public_constants_present():
    assert hasattr(pycreative, 'PROJECT')
    assert hasattr(pycreative, 'SQUARE')
    assert hasattr(pycreative, 'ROUND')
    assert hasattr(pycreative, 'MITER')
    assert hasattr(pycreative, 'BEVEL')


def test_public_constants_map_to_skia():
    assert map_stroke_cap(skia, pycreative.PROJECT) == skia.Paint.kSquare_Cap
    assert map_stroke_cap(skia, pycreative.SQUARE) == skia.Paint.kButt_Cap
    assert map_stroke_cap(skia, pycreative.ROUND) == skia.Paint.kRound_Cap

    assert map_stroke_join(skia, pycreative.MITER) == skia.Paint.kMiter_Join
    assert map_stroke_join(skia, pycreative.BEVEL) == skia.Paint.kBevel_Join
    assert map_stroke_join(skia, pycreative.ROUND) == skia.Paint.kRound_Join
