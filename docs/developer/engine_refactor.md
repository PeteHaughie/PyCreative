Engine refactor — developer notes
================================

This short guide documents the conventions and patterns used in the
recent Engine refactor so future contributors can follow the same
approach.

Why this layout
---------------
- `src/core/engine/impl.py` is a conservative, import-safe headless
  implementation. It delegates to helpers in `src/core/engine/` but
  retains inline fallbacks so tests/examples that import the package
  don't need optional GUI/GPU libs at import time.
- Small implementation modules (for example `frame.py`, `loop.py`,
  `input_simulation.py`) hold focused logic. These modules are imported
  lazily from `impl.py` only when their behaviour is required.

Key conventions
---------------
1. Lazy importing with fallbacks

   Pattern: inside public Engine methods, try to import the helper
   function/class; if that fails, run a small inline fallback.

   Example:

   - try:
       from core.engine.frame import step_frame as _sf
       return _sf(self)
     except Exception:
       # small inline fallback implementation

   Why: avoids import-time dependencies on optional adapters like
   `pyglet`/`skia-python` while still allowing the project to use the
   extracted helpers in richer environments.

2. Small, focused modules

   - `frame.py` — single-frame orchestration (setup/draw ordering,
     headless background handling).
   - `loop.py` — windowed scheduling and event wiring (pyglet handlers).
   - `input_simulation.py` — Engine simulation helpers used by tests.
   - `transforms.py` — matrix stack and transform helpers.
   - `registrations.py` — central API/state registration for color,
     stroke, shape helpers.
   - `presenter.py` / `snapshot.py` — present/replay helpers and
     snapshot backends.

3. Headless-first testing

   - Unit tests (in `tests/`) must be runnable in headless CI. Prefer
     asserting on recorded `GraphicsBuffer.commands` rather than pixel
     equality.
   - Tests should exercise both the delegated helper import path and
     the headless fallback where practical.

4. Minimal top-level side-effects

   - Avoid heavy imports at module import time. Adapter imports like
     `pyglet` or `skia` must be inside functions and guarded with
     try/except.

Developer workflow notes
------------------------
- When extracting behaviour from `impl.py` to a new module:
  - Create the new helper module under `src/core/engine/`.
  - Update `impl.py` to import the new helper lazily, with an inline
    fallback copy of the original behaviour.
  - Add tests that exercise the new helper as well as the fallback.

- Linting and formatting:
  - The repo uses `ruff` and (optionally) `black`. Keep line-length
    at or under 88 chars unless the project agrees to change it.
  - Prefer small, localized edits rather than repo-wide reflows in a
    single PR.

- Debugging runtime/adapter issues:
  - Enable environment variable `PYCREATIVE_DEBUG_HANDLER_EXCEPTIONS=1`
    to re-raise sketch handler exceptions during development.

When to change the pattern
---------------------------
- If a new adapter is required across many modules, consider adding a
  small adapter factory/shim under `src/core/adapters/` and exposing a
  tiny import helper (e.g., `_import_pyglet()`) to centralize error
  handling.
- If the repo adopts a different line-length policy (e.g., 100 cols),
  run an agreed formatting step (black / ruff --fix) in a separate PR
  to keep the refactor PRs focused.

Where to document API changes
----------------------------
- Update `docs/api/` when public APIs change.
- Add integration examples to `examples/` for behaviours that depend on
  windowing/presenters so contributors have runnable specs.

