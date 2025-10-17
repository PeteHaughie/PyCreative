from core.engine.impl import Engine
from core.shape import begin_shape, vertex, end_shape


def test_begin_vertex_end_records_shape():
    eng = Engine(sketch_module=None, headless=True)
    begin_shape(eng, mode='POLYGON')
    vertex(eng, 0, 0)
    vertex(eng, 10, 0)
    vertex(eng, 10, 10)
    vertex(eng, 0, 10)
    end_shape(eng, close=True)

    shapes = [c for c in eng.graphics.commands if c.get('op') == 'shape']
    assert len(shapes) == 1
    s = shapes[0]['args']
    assert s['mode'] == 'POLYGON'
    assert s['close'] is True
    assert s['vertices'] == [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
