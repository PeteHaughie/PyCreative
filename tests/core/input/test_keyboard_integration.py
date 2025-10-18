from core.engine.impl import Engine


class _Sketch:
    def __init__(self):
        self.pressed_calls = []
        self.released_calls = []

    def key_pressed(self, event=None):
        self.pressed_calls.append(event)

    def key_released(self, event=None):
        self.released_calls.append(event)


def test_engine_simulate_key_press_and_release_updates_state_and_calls_handlers():
    s = _Sketch()
    eng = Engine(sketch_module=s, headless=True)

    # simulate press using primitives
    eng.simulate_key_press(key='a')
    assert eng.key == 'a'
    assert eng.key_pressed is True
    assert len(s.pressed_calls) == 1

    # simulate release using primitives
    eng.simulate_key_release(key='a')
    assert eng.key == 'a'
    assert eng.key_pressed is False
    assert len(s.released_calls) == 1

    # simulate press with an event dict (non-ascii key)
    eng.simulate_key_press(event={'key': None, 'key_code': 'LEFT'})
    # Adapter surfaces a Processing-like sentinel for non-printable keys
    assert eng.key == 'CODED'
    assert eng.key_code == 'LEFT'
    assert eng.key_pressed is True
    assert len(s.pressed_calls) == 2

    eng.simulate_key_release(event={'key': None, 'key_code': 'LEFT'})
    assert eng.key_pressed is False
    assert len(s.released_calls) == 2
