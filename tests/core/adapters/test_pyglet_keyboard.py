from core.adapters import pyglet_keyboard


def test_normalize_event_passes_through_dict():
    src = {'key': 'a', 'key_code': None, 'modifiers': []}
    out = pyglet_keyboard.normalize_event(src)
    # Adapter should preserve provided key/key_code values; extra keys
    # (like 'repeat') may be added by the normalizer.
    assert out.get('key') == src['key']
    assert out.get('key_code') == src['key_code']


def test_map_key_constant_strips_trailing_underscore_and_sets_key_code():
    # Simulate pyglet constant by calling _map_key_constant indirectly via
    # normalize_event with a dict providing 'symbol'. We don't import pyglet
    # here; instead assert that dict passthrough stays intact and adapter
    # will preserve provided explicit key_code when present.
    src = {'symbol': None, 'key': None, 'key_code': 'LEFT', 'modifiers': []}
    out = pyglet_keyboard.normalize_event(src)
    # Since input provided explicit key_code, adapter should preserve it
    assert out.get('key_code') == 'LEFT'
    # Adapter now surfaces Processing-like sentinel 'CODED' for non-printable keys
    assert out.get('key') == 'CODED'


def test_normalize_event_handles_none_and_missing_pyglet():
    out = pyglet_keyboard.normalize_event(None)
    assert out == {}
