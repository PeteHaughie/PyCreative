# Copilot Agent Instructions for PyCreative

## Project Overview

PyCreative is a batteries-included creative coding framework for Python, inspired by Processing/openFrameworks, built atop PyGame. It targets artists, educators, and rapid prototypers, providing ergonomic APIs for graphics, input, audio, video, and more. The architecture is modular, supporting easy extension and live-coding workflows.

## Architecture & Key Components

- **pycreative.app**: Main loop, lifecycle hooks (`setup`, `update`, `draw`, `on_event`, `teardown`), frame timing.
- **pycreative.graphics**: Surface wrapper, drawing primitives (`rect`, `ellipse`, `line`, `image`), shader support.
- **pycreative.input**: Unified event abstraction, dispatch to sketch via `on_event`.
- **pycreative.audio/video**: Optional modules for media playback (extras_require).
- **pycreative.assets**: Asset discovery, hot-reload.
```markdown
# Copilot Agent Instructions — PyCreative (condensed)

This file contains the minimal, repo-specific guidance an AI coding agent needs to be productive editing and testing PyCreative.

Key pointers
- Project root: `pyproject.toml` defines the package `pycreative` and the CLI script `pycreative` (entry: `pycreative.cli:main`).
- Primary source: `src/pycreative/` (notable files: `app.py`, `graphics.py`, `input.py`, `cli.py`, `assets.py`).
- Examples: `examples/` contain runnable sketches that double as usage tests (run via the `pycreative` CLI).
- Tests: `tests/` use `pytest`; integration tests are marked with `@pytest.mark.integration` (see `pytest.ini`).

Architecture and important patterns
- `Sketch` (`src/pycreative/app.py`) is the lifecycle entrypoint: override `setup()`, `update(dt)`, `draw()`, `on_event()`, `teardown()`.
- `Surface` (`src/pycreative/graphics.py`) wraps a `pygame.Surface` and centralizes drawing state (fill/stroke/stroke_weight), transform stack, and primitives. Prefer adding primitives here for drawing behavior consistency.
- Input normalization: `src/pycreative/input.py` converts pygame events to `Event` dataclass and calls `sketch.on_event(e)`; default Escape handling is enabled and can be disabled via `self.set_escape_closes(False)`.
- CLI loader: `src/pycreative/cli.py` lazily imports user sketches, detects `main()`/`run()` functions or `Sketch` subclasses and runs them. Use `--headless` to run with `SDL_VIDEODRIVER=dummy`.

Developer workflows (concrete commands)
- Run an example/sketch with the project source on PYTHONPATH (recommended):
  - `pycreative examples/offscreen_example.py`  # uses package entrypoint
  - Or: `python examples/offscreen_example.py`
- Run tests: `pytest tests/` (CI uses the same command). To skip integration tests: `pytest -m "not integration"`.
- Run a single test file: `pytest tests/test_graphics_surface.py`.

Conventions specific to this repo
- Type hints are used across public APIs; prefer typed signatures for new functions.
- Drawing state/behavior: prefer per-call style kwargs on primitives (e.g., `surface.rect(..., fill=(r,g,b), stroke=(r,g,b), stroke_weight=2)`) and implement new features on `Surface` so both on-screen and offscreen surfaces share behavior.
- Pending state: `Sketch` records some state set before the display exists (color_mode, rect/ellipse modes, fill/stroke). When changing sketch behavior, account for pending vs runtime behavior in `Sketch.run()`.
- Tests: avoid requiring an actual display — use the CLI `--headless` behavior (set `SDL_VIDEODRIVER=dummy`) or mock `pygame` APIs. Look at the test helpers in `tests/` for patterns.

Integration points and dependencies
- Required at runtime for local development: `pygame`, `pillow`, `skia-python` (declared in `pyproject.toml`). Optional extras: `sounddevice` (audio), `ffmpeg-python`/`opencv-python` (video).
- OpenGL/Shader support is optional and gated behind availability — add feature flags or optional imports as other modules do.

Small examples to copy when implementing features
- Add a drawing primitive: mirror parameter behavior from existing `rect()`/`ellipse()` in `Surface` (see `graphics.py:rect()`/`ellipse()` ), use `_is_identity_transform()` fast path and transform_points for transformed paths.
- Normalize input events: use `Event.from_pygame()` in `input.py` and call `sketch.on_event(e)`; update `sketch.key`, `sketch.key_code`, `sketch.key_is_pressed` consistently.
- CLI runner: follow `cli.run_sketch()` behavior when loading user modules and prefer graceful error messages (see existing prints and sys.exit codes).

Quality gates (what to run after edits)
- Run: `ruff src/ tests/` (ruff config in `pyproject.toml`).
- Run tests: `pytest -q` and ensure no new integration tests are accidentally unmarked.
- Smoke-run an example: `pycreative examples/offscreen_example.py --headless --max-frames 5` to verify no display dependency and basic runtime behavior.

What to avoid / repo-specific gotchas
- Avoid importing `pygame` at module import time for CLI modules that are used for metadata (see `cli.py` which deliberately delays heavy imports).
- Don't assume numpy-backed pixel arrays; `graphics.PixelView` currently supports nested lists and numpy may be absent (`_HAS_NUMPY = False`). Implement pixel helpers to work without numpy.

If you change public behaviour
- Add/update a unit test in `tests/` (pure logic) and an integration sketch in `examples/` when the change touches rendering or runtime loop behavior.
