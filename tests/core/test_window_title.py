
from core.engine.impl import Engine
from core.engine.api import SimpleSketchAPI


def test_window_title_no_window_does_not_raise():
    # Engine in headless mode has no _window attribute; calling window_title
    # should not raise an exception.
    eng = Engine(sketch_module=None, headless=True)
    api = SimpleSketchAPI(eng)
    # Should simply return or do nothing
    api.window_title('test')


class DummyWin:
    def __init__(self):
        self.caption = None

    def set_caption(self, text):
        self.caption = text


def test_window_title_sets_caption_on_window():
    eng = Engine(sketch_module=None, headless=True)
    # attach a dummy window object
    eng._window = DummyWin()
    api = SimpleSketchAPI(eng)
    api.window_title('hello world')
    assert getattr(eng._window, 'caption') == 'hello world'
