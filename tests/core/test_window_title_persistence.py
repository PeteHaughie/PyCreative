import pytest

from core.engine.impl import Engine


class SketchSetsTitleInSetup:
    def setup(self, this):
        # Set title during setup before a window is created
        this.window_title('persisted title')


def test_window_title_persists_until_window_created(monkeypatch):
    # We will exercise Engine.start() window-creation path but avoid
    # launching a real pyglet app. Monkeypatch pyglet.window.Window to a dummy.

    try:

        class DummyWin:
            def __init__(self, width, height, vsync=True):
                self.width = width
                self.height = height
                self.vsync = vsync
                self.caption = None

            def set_caption(self, text):
                self.caption = text

        # Monkeypatch constructor
        monkeypatch.setattr('pyglet.window.Window', DummyWin)
    except Exception:
        pytest.skip('pyglet not available for this test')

    sketch = SketchSetsTitleInSetup()
    eng = Engine(sketch_module=sketch, headless=False)

    # start() will create a window and should apply the pending title
    # We run start with max_frames=1 to create the window and exit quickly.
    eng.start(max_frames=1)

    assert hasattr(eng, '_window')
    assert getattr(eng._window, 'caption') == 'persisted title'
