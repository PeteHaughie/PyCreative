

class HandlerSketch:
    def __init__(self):
        self.calls = []

    def key_pressed(self, event=None):
        # should be called when a key is pressed; event may be None in some backends
        self.calls.append(('pressed', event))

    def key_released(self, event=None):
        self.calls.append(('released', event))


def test_key_pressed_and_released_handlers_called():
    s = HandlerSketch()
    # Simulate event dispatch (the engine will call these)
    s.key_pressed()
    s.key_released()
    assert ('pressed', None) in s.calls
    assert ('released', None) in s.calls


def test_key_pressed_receives_event_object_when_available():
    s = HandlerSketch()
    evt = {'key': 'a', 'key_code': None}
    s.key_pressed(evt)
    assert ('pressed', evt) in s.calls


def test_key_released_receives_event_object_when_available():
    s = HandlerSketch()
    evt = {'key': None, 'key_code': 'LEFT'}
    s.key_released(evt)
    assert ('released', evt) in s.calls
