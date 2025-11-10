import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from core.engine.impl import Engine
from core.engine.loop import setup_window_loop


class FakePyglet(types.ModuleType):
    def __init__(self, name='pyglet'):
        super().__init__(name)
        class _Clock:
            def schedule(self, fn):
                return None
            def schedule_interval(self, fn, interval):
                return None

        class _App:
            def run(self):
                return None
            def exit(self):
                return None

        self.clock = _Clock()
        self.app = _App()


class FakeWindow:
    def __init__(self, pixel_ratio=2.0):
        self._events = {}
        self._pixel_ratio = pixel_ratio

    def event(self, fn):
        self._events[fn.__name__] = fn
        return fn

    def get_pixel_ratio(self):
        return float(self._pixel_ratio)


class FakePresenter:
    def __init__(self, width=200, height=200):
        self.width = width
        self.height = height
        # simulate backing size and logical size
        self._backing_size = (width, height)
        self._logical_size = (int(width / 2), int(height / 2))

    def resize(self, w, h):
        # record a resize request
        self.width = int(w)
        self.height = int(h)


def test_mouse_scaling_with_presenter():
    # Ensure importing pyglet inside setup_window_loop succeeds by stubbing
    fake = FakePyglet('pyglet')
    sys.modules['pyglet'] = fake

    # Make a trivial sketch module (setup/draw not required)
    import importlib.util
    from tempfile import TemporaryDirectory
    from pathlib import Path

    with TemporaryDirectory() as td:
        p = Path(td) / 'sketch.py'
        p.write_text('def draw(this):\n    pass\n', encoding='utf-8')
        spec = importlib.util.spec_from_file_location('examples.temp.sketch', str(p))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)

        eng = Engine(sketch_module=m, headless=False)

        # attach fake window and presenter
        win = FakeWindow(pixel_ratio=2.0)
        eng._window = win
        presenter = FakePresenter(width=400, height=200)

        # Register handlers; setup_window_loop will probe window.get_pixel_ratio
        setup_window_loop(eng, presenter)

        # ensure the handler was registered
        fn = win._events.get('on_mouse_motion')
        assert fn is not None

        # Call with backing-pixel coords (200,100) -> logical coords (100,50)
        fn(200, 100, 0, 0)

        # engine should have scaled coords: mouse_x = 100, mouse_y = hy - 50
        hy = int(getattr(eng, 'height', 200))
        assert int(getattr(eng, 'mouse_x', -1)) == 100
        assert int(getattr(eng, 'mouse_y', -1)) == (hy - 50)

    # cleanup stub
    sys.modules.pop('pyglet', None)


if __name__ == '__main__':
    test_mouse_scaling_with_presenter()
    print('integration test ran OK')
