
# Pre-development tests for keyboard API behaviour described in docs/api/input/keyboard

class DummySketch:
    """A minimal sketch-like object used to exercise Engine input bindings in unit tests.

    We don't import Engine here; these tests are behavioural contracts that the
    Engine should satisfy later. Keep tests small and deterministic.
    """
    def __init__(self):
        # system variables
        self.key = None
        self.key_code = None
        self.key_pressed = False
        self._events = []

    # helpers tests will call to simulate framework events
    def _press_key(self, key, key_code=None):
        self.key = key
        self.key_code = key_code
        self.key_pressed = True
        self._events.append(('press', key, key_code))



    class DummySketch:
        """A minimal sketch-like object used to exercise Engine input bindings in unit tests.

        These are small, deterministic helpers used by pre-development tests
        that express the expected behaviour of the system variables.
        """
        def __init__(self):
            # system variables
            self.key = None
            self.key_code = None
            self.key_pressed = False
            self._events = []

        # helpers tests will call to simulate framework events
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
        # simulate pressing a non-ASCII key: e.g. LEFT_ARROW
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
        # BACKSPACE should be available via key variable
        s._press_key('BACKSPACE')
        assert s.key == 'BACKSPACE'
        assert s.key_code is None

        s._release_key('BACKSPACE')
        assert s.key == 'BACKSPACE'


    def test_key_case_insensitive_example_behaviour():
        s = DummySketch()
        # Example in docs checks key == 'b' or key == 'B'
        s._press_key('b')
        assert s.key in ('b', 'B')
        s._release_key('b')
        s._press_key('B')
        assert s.key in ('b', 'B')
