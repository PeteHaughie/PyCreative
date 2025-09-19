Prompt: start with **Task A — Project skeleton**

Use these exact prompts to request focused work from the AI:

1. "Implement `pycreative.app.Sketch` with a PyGame main loop, lifecycle hooks, and frame timing. Include tests and `examples/hello_sketch.py` that runs headless for 3 frames."
2. "Create `pycreative.graphics.Surface` that wraps pygame.Surface and add drawing helpers: `rect`, `ellipse`, `line`, and `image`. Add unit tests that mock the underlying surface."
3. "Add a `pycreative.input` module that normalizes PyGame events into `Event` dataclasses and dispatches `on_event` to the sketch. Provide `examples/input_demo.py`."
4. "Add `pyproject.toml` with `[project]` metadata, `extras_require` for video/audio, and CI workflow to run tests on push."

# Copilot Instructions

## Project Overview

> A fully-featured Python creative-coding framework built on top of PyGame, designed for artists, educators, and rapid prototyping. Think Processing/openFrameworks ergonomics with Python simplicity and PyGame performance.

---

## 1. Overview / Vision

PyCreative is a batteries-included creative-coding framework that makes it trivial to build visual, audio, and interactive projects in Python while staying lightweight and extensible. It uses PyGame for low-level drawing, input, and window/context management, but provides higher-level conveniences: a component-driven app loop, scene & state management, easy shader support, multimedia I/O, asset management, utilities for math & noise, tight integration for live-coding, and idiomatic Python APIs inspired by Processing and openFrameworks.

A creative coding environment for visual artists to build interactive installations using Python and Pygame.
It must have a modular architecture to allow easy addition of new features and components.
Support for opening multiple video files is essential.
UVC webcam and video capture device support is essential.
Audio playback and control are essential.
Audio reactive features are essential.
Midi input support is essential.
Dynamic resolution switching is a must.
Must have support for glsl shaders.
Must have supprot for 3D rendering.
Must have support for 2D rendering.
Must have support for 2D vector graphics.
Must have support for text rendering.
Must have support for image loading and display.
Must have support for basic geometric shapes (rectangles, circles, lines).
Must have support for user input (keyboard, mouse, midi controllers).

Primary audience: educators, artists, hobbyists, prototypers, interactive-installation developers.

Design goals:
- **Simplicity:** One-file sketches should be easy to author and run.
- **Power:** Support full applications with modular components and plugins.
- **Performance:** Efficient drawing and resource handling; optional C-extension hooks later.
- **Extensibility:** Plugin architecture, add-ons, and user-written modules.
- **Discoverability:** Clear docs, examples, and API parity with Processing/openFrameworks where it helps.

---

## 2. High-level Feature List

### Core runtime
- `Sketch` / `App` class with lifecycle hooks: `setup()`, `update(dt)`, `draw()`, `on_event(event)`, `teardown()`
- Declarative and imperative APIs for drawing primitives (line, rect, ellipse, path)
- Layered rendering with `Surface` objects, easy FBO-like render targets
- Built-in frame timing, FPS manager, and step/scrub controls

### Input & Interaction
- Keyboard, mouse, multi-touch, gamepad, and joystick support via PyGame events
- Gesture helpers (drag, pinch, double-tap)
- Easy mapping from input to UI controls and OSC or network messages

### Graphics
- 2D and basic 3D primitives (camera, transform stack) built over PyGame surfaces and optional OpenGL backend
- High-level image and texture loaders, sprite sheets
- Simple GLSL shader wrapper for fragment/vertex shaders (optional OpenGL context)
- Blend modes, alpha, masks, and post-processing passes

### Audio & Media
- Audio playback and recording wrappers (play, pause, seek) using PyGame.mixer and optional integration with sounddevice/pyalsa
- Video playback via ffmpeg wrappers (decoding frames into Surfaces)

### Time, Math & Utilities
- Routines for easing, interpolation, mapped ranges, noise (Perlin / Simplex), random distributions
- Timelines, tweens, schedulers, and coroutines

### Scenes & UI
- Scene manager and simple GUI widgets (buttons, sliders, toggles) designed for live-coding and quick interfaces
- Inspectable `Properties` for debugging and exposing parameters

### Asset Management
- Project `data/` discovery, hot-reloading of assets during development
- Asset pack support for bundling images, audio, fonts

### Tools for artists & educators
- Live-reload mode (auto-restart or hot-replace code while preserving state where possible)
- One-command packaging to an executable + data bundle
- Starter templates and a gallery of example sketches

---

## 3. Architecture & Module Breakdown

Top-level package: `pycreative`

Suggested subpackages/modules:

- `pycreative.app` — `App/Sketch` core: lifecycle, main loop, event dispatch
- `pycreative.graphics` — drawing primitives, Surfaces, render pipeline, shaders
- `pycreative.input` — event abstractions, gesture recognizers
- `pycreative.audio` — audio playback, capture, simple synthesis helpers
- `pycreative.video` — video decoding, frame-to-surface utilities
- `pycreative.assets` — asset discovery, caching, hot-reload
- `pycreative.math` — easing, noise, interpolation, transform helpers
- `pycreative.ui` — widgets, inspector, layout helpers
- `pycreative.timing` — Tween, Timeline, Coroutine helpers
- `pycreative.plugins` — plugin API to register new features
- `pycreative.examples` — curated examples and templates
- `pycreative.cli` — command line tools: run, build, package, new
- `pycreative.tests` — unit & integration tests

Each module should have a clear public API surface and internal helpers. Modules should be importable individually (e.g., `from pycreative.graphics import Surface`) so users can adopt bits without the whole framework.

---

## 4. API Sketches / Examples

### Minimal sketch (one-file)
```py
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
```py
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

APIs should be small, discoverable, and chainable where it makes sense.

---

## 5. Copilot (AI) Implementation Instructions

This section is the `copilot-instructions.md` portion to be used by an AI coding assistant. The goal: break the framework into deliverable tasks and instruct the AI to implement modules, tests, examples, docs, and CI.

---

## 6. Detailed Task Breakdown

Below are executable tasks. Treat each as a separate commit/PR.

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

---

## 8. Contribution & Code Review Guidelines for Copilot PRs

- Keep PRs small (one feature or bugfix per PR).
- Each PR must include: description, files changed, tests added, manual test steps.
- Run linters and unit tests locally before requesting review.
- Include docstrings and update module `README.md`.

---

## 9. Delivery Checklist (what the copilot should mark done)

- [ ] Project skeleton and packaging
- [ ] `pycreative.app` MVP with examples & tests
- [ ] `pycreative.graphics` MVP
- [ ] `pycreative.input` MVP
- [ ] CLI runner
- [ ] 12 examples and module readmes
- [ ] CI, linters, and `pyproject.toml`
- [ ] Basic docs and changelog

---

## 10. Key Files & Directories

- `README.md`: Project overview and setup.
- `examples/`: Example sketches.
- `sketches`: User-created sketches.
- `src/`: Main source code.
- `tests/`: Test suite.

*End of file.*
