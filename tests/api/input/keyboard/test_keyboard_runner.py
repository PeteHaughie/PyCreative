
# Consolidated clean runner for keyboard pre-development tests.

class DummySketch:
    def __init__(self):
        self.key = None
        self.key_code = None
        self.key_pressed = False
        self._events = []

    def _press_key(self, key, key_code=None):
        self.key = key
        self.key_code = key_code
        self.key_pressed = True
        self._events.append(('press', key, key_code))

    def _release_key(self, key, key_code=None):
        self.key = key
        self.key_code = key_code
        self.key_pressed = False
        self._events.append(('release', key, key_code))


def test_key_variable_updates_on_press_and_release():
    s = DummySketch()
    assert s.key is None

    s._press_key('a')
    assert s.key == 'a'
    assert s.key_pressed is True

    s._release_key('a')
    assert s.key == 'a'
    assert s.key_pressed is False


def test_non_ascii_uses_key_code():
    s = DummySketch()
    s._press_key(None, key_code='LEFT')
    assert s.key is None
    assert s.key_code == 'LEFT'
    assert s.key_pressed is True

    s._release_key(None, key_code='LEFT')
    assert s.key is None
    assert s.key_code == 'LEFT'
    assert s.key_pressed is False


def test_ascii_special_keys_in_key_variable():
    s = DummySketch()
    s._press_key('BACKSPACE')
    assert s.key == 'BACKSPACE'
    assert s.key_code is None

    s._release_key('BACKSPACE')
    assert s.key == 'BACKSPACE'


def test_key_case_insensitive_example_behaviour():
    s = DummySketch()
    s._press_key('b')
    assert s.key in ('b', 'B')
    s._release_key('b')
    s._press_key('B')
    assert s.key in ('b', 'B')


class HandlerSketch:
    def __init__(self):
        self.calls = []

    def key_pressed(self, event=None):
        self.calls.append(('pressed', event))

    def key_released(self, event=None):
        self.calls.append(('released', event))


def test_key_pressed_and_released_handlers_called():
    s = HandlerSketch()
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
