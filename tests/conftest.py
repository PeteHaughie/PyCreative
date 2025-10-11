import pytest
import sys


@pytest.fixture
def no_skia(monkeypatch):
    """Fixture that ensures the 'skia' module is not importable.

    Use this in Red tests that need to simulate absence of skia. It removes
    'skia' from sys.modules and injects a sentinel to prevent accidental import.
    """
    sentinel = object()
    monkeypatch.setitem(sys.modules, 'skia', None)
    yield
    # teardown handled by monkeypatch


@pytest.fixture
def isolated_monkeypatch(monkeypatch):
    """Wrapper around monkeypatch — use this to make intent explicit."""
    yield monkeypatch


@pytest.fixture
def fail_after():
    """Return a context manager that raises TimeoutError after N seconds.

    Uses signal.alarm so it works for blocking calls on Unix-like systems. Use
    as:

        with fail_after(3):
            blocking_call()

    Note: signal.alarm only works on the main thread.
    """
    import signal
    import contextlib

    @contextlib.contextmanager
    def _fail_after(seconds: int):
        if seconds is None or seconds <= 0:
            yield
            return

        def _handler(signum, frame):
            raise TimeoutError(f'Test exceeded {seconds} seconds')

        old_handler = signal.signal(signal.SIGALRM, _handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    return _fail_after
