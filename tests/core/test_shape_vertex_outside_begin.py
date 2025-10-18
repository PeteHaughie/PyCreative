import logging
from core.shape import vertex
from core.engine.impl import Engine


def test_vertex_outside_begin_logs_warning(caplog):
    caplog.set_level(logging.WARNING)
    eng = Engine(sketch_module=None, headless=True)
    # call vertex directly without begin_shape
    vertex(eng, 10, 20)
    # ensure we logged a warning
    assert any('vertex called outside begin_shape' in r.message for r in caplog.records)
