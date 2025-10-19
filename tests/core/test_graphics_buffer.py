from core.graphics import GraphicsBuffer


def test_graphics_buffer_record_and_seq():
    buf = GraphicsBuffer()
    assert buf.commands == []
    buf.record('rect', x=1, y=2)
    buf.record('circle', x=3, y=4)
    assert len(buf.commands) == 2
    assert buf.commands[0]['op'] == 'rect'
    assert buf.commands[1]['op'] == 'circle'
    # sequence numbers increment starting at 1
    assert buf.commands[0]['meta']['seq'] == 1
    assert buf.commands[1]['meta']['seq'] == 2


def test_graphics_buffer_clear_and_continue_seq():
    buf = GraphicsBuffer()
    buf.record('point', x=0, y=0)
    first_seq = buf.commands[0]['meta']['seq']
    buf.clear()
    assert buf.commands == []
    # recording after clear should continue incrementing seq
    buf.record('line', x1=0, y1=0, x2=1, y2=1)
    assert len(buf.commands) == 1
    assert buf.commands[0]['meta']['seq'] == first_seq + 1
