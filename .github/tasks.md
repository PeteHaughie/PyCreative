### Task A — Project skeleton
- Files: `pyproject.toml`, `README.md`, `LICENSE` (MIT), `.gitignore`, `pycreative/__init__.py`
- Minimal CI: GitHub Actions `ci.yml` that runs `pip install -e .[test]` then `pytest` and linters.

### Task B — Implement `pycreative.app`
- Files: `pycreative/app.py`, `pycreative/__init__.py` exports `Sketch`
- Behavior: `Sketch` should provide `setup()`, `update(dt)`, `draw()`, `on_event(e)` hooks and manage PyGame initialization, window creation, main loop, and frame timing.
- Tests: instantiate a minimal subclass and run loop for 3 frames in headless mode.
- Example: `examples/hello_sketch.py`.

### Task C — Implement `pycreative.graphics`
- Files: `pycreative/graphics.py`, `examples/graphics_demo.py`
- Implement `Surface` wrapper and drawing helpers.
- Tests for coordinate math and basic drawing calls (mock out actual surface draws).

### Task D — Implement `pycreative.input`
- Files: `pycreative/input.py`, `examples/input_demo.py`
- Provide unified `Event` class and `on_event` dispatching.

### Task E — CLI
- Files: `pycreative/cli.py`, `entry_points` in `pyproject.toml`
- Provide `pycreative run path/to/file.py` to run a sketch.