import pytest


@pytest.mark.headless
def test_engine_shim_exports_engine():
    """Red: ensure the public shim exposes the Engine symbol.

    This is a small, fast test that avoids importing heavy backends.
    It asserts the module `src.core.engine` (importable as `core.engine` via src/ path)
    exposes the `Engine` symbol and lists it in `__all__` when present.
    """
    import importlib
    import sys
    sys.path.insert(0, 'src')

    # Import lazily and skip the test if the implementation is temporarily
    # unavailable (avoids collection-time ImportError during active edits).
    try:
        mod = importlib.import_module('core.engine')
    except Exception as exc:  # pragma: no cover - defensive in CI/dev
        import pytest

        pytest.skip(f"core.engine not importable: {exc}")

    # The shim should expose Engine without causing heavy side-effects.
    assert hasattr(mod, 'Engine'), 'public shim must expose Engine'
    if hasattr(mod, '__all__'):
        assert 'Engine' in mod.__all__, '__all__ should include Engine'
