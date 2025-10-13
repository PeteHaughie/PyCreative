from core.engine import Engine


class DummyWindow:
    def __init__(self):
        self.size_calls = []

    def set_size(self, w, h):
        self.size_calls.append((w, h))


def test_set_size_updates_engine_and_window():
    eng = Engine(headless=True)
    # attach dummy window to simulate windowed environment
    dummy = DummyWindow()
    eng._window = dummy

    eng._set_size(320, 240)

    assert eng.width == 320
    assert eng.height == 240
    assert dummy.size_calls == [(320, 240)]
