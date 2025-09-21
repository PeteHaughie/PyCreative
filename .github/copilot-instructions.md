

# Copilot Agent Instructions for PyCreative

## Project Overview

PyCreative is a batteries-included creative coding framework for Python, inspired by Processing/openFrameworks, built atop PyGame. It targets artists, educators, and rapid prototypers, providing ergonomic APIs for graphics, input, audio, video, and more. The architecture is modular, supporting easy extension and live-coding workflows.

## Architecture & Key Components

- **pycreative.app**: Main loop, lifecycle hooks (`setup`, `update`, `draw`, `on_event`, `teardown`), frame timing.
- **pycreative.graphics**: Surface wrapper, drawing primitives (`rect`, `ellipse`, `line`, `image`), shader support.
- **pycreative.input**: Unified event abstraction, dispatch to sketch via `on_event`.
- **pycreative.audio/video**: Optional modules for media playback (extras_require).
- **pycreative.assets**: Asset discovery, hot-reload.
- **pycreative.ui**: Basic widgets (Slider, Button).
- **pycreative.timing**: Tween, Timeline utilities.
- **examples/**: Runnable sketches demonstrating features.
- **tests/**: Unit and integration tests (pytest).

## Developer Workflows

- **Run a sketch:** `python examples/hello_sketch.py`
- **Run tests:** `pytest tests/`
- **Debug:** Use `pdb` or IDE debugger.
- **Extend primitives:** Add to `pycreative.graphics.Surface`.
- **Add input features:** Extend `pycreative.input` and event dataclasses.


## Conventions & Patterns

- **API design:** APIs should be small, discoverable, and chainable where it makes sense. See examples below.
- **Imports:** All modules importable individually (e.g., `from pycreative.graphics import Surface`).
- **Naming:** snake_case for functions/variables, CamelCase for classes.
- **Style:** PEP8, Black, Ruff, Isort. Type hints everywhere. Dataclasses for value types.
- **Docstrings:** All public APIs require docstrings and usage examples.
- **Tests:** Pure logic: unit tests. PyGame-dependent: integration tests, mark separately.

## Example API Usage

### Minimal sketch (one-file)
```python
from pycreative import Sketch

class MySketch(Sketch):
	def setup(self):
		self.size(800, 600)
		self.bg = 0

	def update(self, dt):
		pass

	def draw(self):
		self.clear(self.bg)
		self.ellipse(self.width/2, self.height/2, 200, 200)

if __name__ == '__main__':
	MySketch().run()
```

### App with state and a shader
```python
from pycreative import Sketch, Shader

class Flow(Sketch):
	def setup(self):
		self.size(1280, 720, fullscreen=False)
		self.shader = Shader(fragment='shaders/flow.frag')

	def draw(self):
		self.shader.bind({'time': self.t})
		self.rect(0,0,self.width,self.height)
		self.shader.unbind()
```

## Integration Points

- **PyGame**: Required for graphics and input.
- **OpenGL**: Optional, for advanced rendering and shaders.
- **Audio/Video**: Optional, extras_require in packaging.

## CI & Packaging

- GitHub Actions workflows: `ci.yml` (lint, test, docs), `publish.yml` (PyPI).
- Packaging: `setup.cfg` or `pyproject.toml` (minimal required dependencies, extras for video/audio).

## Security & Safety

- No remote code execution during install/runtime.
- Native extensions/features are opt-in only.

---

**Feedback requested:**
Are any architectural details, workflows, or conventions unclear or missing? Let me know if you need more specifics on any module, pattern, or integration point.

### Rules & Constraints
- Use idiomatic, modern Python 3.11+ (type hints, dataclasses where useful).
- Keep dependencies minimal: PyGame is required; optional extras must be behind `extras_require` in `setup.cfg`/`pyproject.toml` (e.g., `video`, `audio`, `opengl`).
- All public APIs must be documented with docstrings and a short usage example.
- Follow PEP8 and Black formatting. Only use ruff.
- Write unit tests using `pytest`. Focus on pure logic first; use integration tests for PyGame-dependent features but mark them separately.
- Follow the simplistic API designs of Processing and openFrameworks where applicable.
- Every class must have a corresponding test in the test suite.
-Documentation for each class and public API must be updated regularly, especially when new features are added or APIs change.

### Development workflow for the AI
For each top-level module, the copilot should:
1. Create the package folder and `__init__.py` exposing the public API.
2. Add typed skeletons for classes and functions with docstrings.
3. Implement the core logic and minimal tests.
4. Provide at least one runnable example that uses the implemented API.
5. Add a `README.md` for the module with a short tutorial.

### High-priority tasks (iteration 0 — MVP)
1. `pycreative.app` — implement `Sketch` with PyGame loop and lifecycle hooks. Support `size()`, `run()`, `clear()`, `frame_rate`.
2. `pycreative.graphics` — implement `Surface` wrapper over PyGame `Surface`, and primitives: `line`, `rect`, `ellipse`, `image`.
3. `pycreative.input` — unify keyboard & mouse events and a simple `on_event` dispatch.
4. CLI: `pycreative PATH/TO/sketch.py` to run a sketch.
5. Tests & examples for each.

### Medium-priority tasks (iteration 1)
- Asset loader with `pycreative.assets` and hot-reload.
- Simple `pycreative.timing` with `Tween` and `Timeline`.
- If no framerate is set, default to 60 FPS.
- All animations should use an in-built delta time mechanism.
- Basic UI widgets (Slider, Button) under `pycreative.ui`.

### Nice-to-have (iteration 2)
- Shader support using PyGame+OpenGL or `moderngl` when available.
- Video decoding via ffmpeg subprocess to frames.
- Audio wrappers with optional `sounddevice` integration.
- Packaging CLI to create a single-folder distribution.

### Implementation details & acceptance criteria
For every implemented module or feature, the copilot must provide the following deliverables:
- Source files in the proper package layout.
- A unit test file that covers key behavior (pass rate >= 90% for unit-tested logic).
- A short example script (under `examples/`) that demonstrates usage and can be run with `python examples/name.py`.
- Module-level README with rationale and API highlights.
- A CHANGELOG entry and a single-line release note.

### Testing strategy
- Use `pytest` for unit tests.
- Use mocking for PyGame where appropriate (e.g., mock `pygame.init()` calls) so tests can run in CI without display.
- Provide one integration test that runs the app loop for a few frames in headless mode.

### Coding & style
- Use type hints everywhere for public functions and classes.
- Use dataclasses for small value types (e.g., `Color`, `Point`).
- Add `pyproject.toml` configured for `black`, `ruff`, `isort`, and `pytest`.

### Documentation & examples
- Build a `docs/` folder with a getting-started guide and API reference (markdown is fine).
- Create 12 example sketches grouped by category: Basics, Input, Graphics, Audio, Video, Shaders, UI, Asset hot-reload, Tweening, Packaging, Live-reload, Advanced.
- Each example must have instructions on how to run and a screenshot (placeholder) in the examples folder.

### CI & Packaging
- Add GitHub Actions workflows: `ci.yml` (lint, test, build docs), `publish.yml` (publish to PyPI on tag)
- Provide `setup.cfg` or `pyproject.toml` and a simple `setup.py` wrapper for backwards compatibility.

### Issue & PR templates
- Provide templates that describe what to include in issues and PRs (summary, steps to reproduce, expected vs actual, tests added).

### Security & Safety
- Do not include any code that executes remote code during install or runtime.
- Avoid default inclusion of native extensions; optional features must be opt-in.
