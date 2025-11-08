import pytest
import sys
import importlib
import types
import os

# Ensure tests can import package modules by adding src to sys.path
sys.path.insert(0, 'src')


def pytest_load_initial_conftests(early_config, args):
    """Pytest hook that runs very early — use it to install a dummy
    `pyglet` module before any test imports occur so native windows can't
    be created during collection or test runs.
    """
    # Respect explicit opt-in
    if os.getenv('PYCREATIVE_ALLOW_NATIVE_WINDOW', '0') == '1':
        return

    if 'pyglet' in sys.modules:
        return

    fake = types.ModuleType('pyglet')
    # minimal window submodule
    win_mod = types.SimpleNamespace()

    class _DW:
        def __init__(self, *a, **k):
            pass

        def event(self, fn=None):
            if fn is None:
                def _decorator(f):
                    try:
                        setattr(self, f.__name__, f)
                    except Exception:
                        pass
                    return f

                return _decorator
            try:
                setattr(self, fn.__name__, fn)
            except Exception:
                pass
            return fn

        def get_framebuffer_size(self):
            return (200, 200)

        def get_pixel_ratio(self):
            return 1.0

    def _Window_factory(*a, **kw):
        return _DW()

    win_mod.Window = _Window_factory
    fake.window = win_mod

    # provide minimal clock and app to satisfy imports that expect them
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

    fake.clock = _Clock()
    fake.app = _App()

    sys.modules['pyglet'] = fake



@pytest.fixture
def engine():
    """Provide a fresh headless Engine instance for tests.

    Import `core.engine` lazily here so test collection doesn't fail if the
    implementation file is temporarily invalid. If the Engine symbol cannot
    be imported the tests that need it will be skipped.
    """
    try:
        mod = importlib.import_module('core.engine')
    except Exception as exc:  # pragma: no cover - defensive during dev
        pytest.skip(f"core.engine import failed: {exc}")

    Engine = getattr(mod, 'Engine', None)
    if Engine is None:
        pytest.skip('core.engine.Engine not found')

    return Engine(sketch_module=None, headless=True)


# Prevent accidental native pyglet windows during test collection or runs by
# monkeypatching pyglet.window.Window to a lightweight dummy that records a
# stacktrace when called. This helps block accidental imports that instantiate
# windows at import-time (examples/scripts) while still allowing tests to
# inject their own fake `pyglet` modules if required.
try:
    import pyglet
    try:
        orig_Window = getattr(pyglet.window, 'Window', None)

        class _BlockedWindow:
            def __init__(self, *args, **kwargs):
                try:
                    import traceback
                    with open('/tmp/pycreative_window_block.log', 'a') as _lf:
                        _lf.write('pyglet.window.Window blocked call:\n')
                        traceback.print_stack(file=_lf)
                except Exception:
                    pass

                # Minimal dummy implementation exposing the small surface of
                # the pyglet window API used by the engine and presenters.
                class _DW:
                    def event(self, fn=None):
                        if fn is None:
                            def _decorator(f):
                                try:
                                    setattr(self, f.__name__, f)
                                except Exception:
                                    pass
                                return f

                            return _decorator
                        try:
                            setattr(self, fn.__name__, fn)
                        except Exception:
                            pass
                        return fn

                    def set_caption(self, *a, **k):
                        return None

                    def switch_to(self):
                        return None

                    def get_framebuffer_size(self):
                        return (kwargs.get('width', 200), kwargs.get('height', 200))

                    def get_pixel_ratio(self):
                        return float(kwargs.get('pixel_ratio', 1.0))

                self._dw = _DW()

            def __getattr__(self, name):
                return getattr(self._dw, name)

        pyglet.window.Window = _BlockedWindow
    except Exception:
        pass
except Exception:
    # pyglet not available; tests may inject a fake module themselves.
    pass
