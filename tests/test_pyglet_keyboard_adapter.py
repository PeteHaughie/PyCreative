import pytest

from core.adapters.pyglet_keyboard import normalize_event
from pyglet.window import key as K


class DummyEvent:
    def __init__(self, k):
        # pyglet events expose both 'key' and 'symbol' in different contexts
        self.key = k
        self.symbol = k
        self.modifiers = None
        self.repeat = False


@pytest.mark.parametrize("name", ["UP", "DOWN", "LEFT", "RIGHT"])
def test_arrow_keys_normalize_to_canonical_key_code(name):
    """Ensure arrow keys produce canonical key_code (no MOTION_* aliases).

    Regression test for mappings where platforms expose both MOTION_UP and UP
    with the same numeric value; we prefer the short canonical name.
    """
    val = getattr(K, name)
    ev = DummyEvent(val)
    out = normalize_event(ev)
    assert out.get("key_code") == name
    # For non-printable special keys we expose 'CODED' as the printable key
    assert out.get("key") == "CODED"


def test_printable_char_preserved():
    class E:
        def __init__(self):
            self.key = 'a'
            self.symbol = 'a'
            self.modifiers = None
            self.repeat = False

    out = normalize_event(E())
    assert out.get('key') == 'a'
    assert out.get('key_code') in (None, 'a')
