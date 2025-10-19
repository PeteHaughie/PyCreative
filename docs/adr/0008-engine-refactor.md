# ADR 0008 — Engine implementation split and headless-first helpers

Status: Accepted

Date: 2025-10-19

Context
-------
The original `Engine` implementation lived in a single, monolithic
module (`src/core/engine/impl.py`). Over time this file grew to include
windowing/loop wiring, input handlers, transform helpers, snapshot
helpers, presenter creation and testing helpers. This made the file
hard to navigate, review, test, and reason about; it also increased
risk when adding adapter-specific imports (pyglet, skia) at module
import time — making headless test runs brittle.

Decision
--------
Split the big `Engine` implementation into small, focused modules under
`src/core/engine/` and keep `impl.py` as the lightweight headless
implementation that delegates to these helpers. The split follows the
extract-by-delegation pattern: each responsibility has a small helper
module (for example `frame.py`, `loop.py`, `input_simulation.py`,
`transforms.py`, `registrations.py`, `snapshot.py`, `presenter.py`).

Key rules for the refactor
- Use lazy imports inside functions so optional/pluggable adapters
  (pyglet, skia, platform-specific adapters) are imported only when
  needed.
- Preserve an inline fallback implementation in `impl.py` for each
  delegated function so the codebase remains import-safe for headless
  tests and early boot paths.
- Keep public shims stable: small `__init__.py` shims re-export public
  API surfaces, while implementation details live in submodules.
- Tests-first workflow: add or update tests during refactor (headless
  behaviours are explicitly tested by `tests/core` so the fallbacks
  remain functional).

Rationale
---------
- Smaller modules are easier to read, test, and maintain.
- Lazy imports + inline fallbacks preserve the headless-first design
  and avoid import-time side effects from optional GUI/GPU libs.
- The split enables clearer responsibilities (loop scheduling vs frame
  orchestration vs input handling vs presenter plumbing) and makes it
  easier to add alternate implementations or platform adapters.

Consequences
------------
- Pro: Improved maintainability, faster developer feedback when editing
  small modules, and safer tests/CI due to reduced import-time surface.
- Pro: Enables adapter-specific implementations (e.g. different
  presenter backends) to be swapped with minimal changes.
- Con: More files to navigate; contributors must follow the lazy-import
  + fallback convention to avoid reintroducing import-time side-effects.

Migration notes
---------------
- New helpers should follow the pattern: try to import the extracted
  implementation, else run a small inline fallback in `impl.py`.
- Update `docs/` and `specs/` when public API surfaces change; prefer
  short, stable re-exports (see `docs/api/` and `src/core/*` shims).

Further work
------------
- Consider consolidating line-length/formatting rules and running an
  automated reformat (black/ruff --fix) repo-wide after agreeing on the
  policy.
- Add architectural tests that run in CI verifying that the headless
  fallbacks are exercised in unit tests (record/replay of graphics
  commands).

Signed-off-by: engine refactor
