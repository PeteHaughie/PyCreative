import pytest
from core.adapters.skia_gl_present import SkiaGLPresenter


def test_variant_order_default():
    p = SkiaGLPresenter(10, 10)
    order = p._variant_ordering(force_gles_override=False, sniff_override=False)
    assert order == ['150', 'es300', '120']


def test_variant_order_force_gles():
    p = SkiaGLPresenter(10, 10, force_gles=True)
    order = p._variant_ordering(force_gles_override=True)
    assert order == ['es300', '150', '120']


def test_variant_order_sniff_override():
    p = SkiaGLPresenter(10, 10)
    order = p._variant_ordering(sniff_override=True)
    assert order == ['es300', '150', '120']
