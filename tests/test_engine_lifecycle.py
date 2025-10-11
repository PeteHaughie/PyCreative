"""Tests for Engine lifecycle (TDD starter - Red).

This test asserts the minimal Engine contract we expect to drive development:
- an `Engine` class in `src.core.engine`
- instance methods `start`, `stop`, and `register_api`.

Write the minimal failing test first (Red). Implementations should make this pass.
"""

import importlib


def test_engine_lifecycle_interface():
    """Red: engine should expose an Engine class with lifecycle hooks."""
    engine = importlib.import_module("src.core.engine")
    assert hasattr(engine, "Engine"), "Engine class not defined in src.core.engine"
    Inst = getattr(engine, "Engine")
    # Creating an instance may require no args; if it requires args the test will error
    inst = Inst()
    for method in ("start", "stop", "register_api"):
        assert hasattr(inst, method), f"Engine missing method {method}"
