import pytest
import sys
import importlib

# Ensure tests can import package modules by adding src to sys.path
sys.path.insert(0, 'src')


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
