```markdown
# ADR 0002 — Public shims and core package split

Status: Proposed

Context
-------
We are reorganising the PyCreative codebase so the public API surface defined
in `specs/python-organisation-refactor` is stable and ergonomic for users,
while the implementation lives under `src/core/` and `src/api/` packages that
can be refactored internally without breaking imports in user sketches.

Two related goals drove the recent work:

- Provide small, import-safe top-level shims (under `src/pycreative`) so
  sketches can `from pycreative import size, background, rect` without
  importing internal modules or triggering heavy GPU/window libraries at
  import time.
- Split up the large engine/impl surface into focused packages under
  `src/core/` (input/, events/, graphics/, io/, shape/, image/, math/, time/, typography/)
  to make future refactors and adapters (for Skia, OpenGL) straightforward.

Decision
--------
1. Add a tiny `src/pycreative/__init__.py` that exposes the stable public API
   as small shim functions and helpers. The shims do not implement behaviour
   themselves; they delegate to a currently-registered Engine instance using
   `set_current_engine(engine)` / `get_current_engine()`.

2. Keep the shim module intentionally minimal and lazy: avoid importing
   GUI, GL, or adapter libraries at shim import time. When necessary, the
   shim will construct a small `SimpleSketchAPI(engine)` helper or access
   explicit engine methods to perform the delegated action.

3. Create the package skeleton under `src/core/` (input, events, graphics,
   io, shape, image, math, time, typography). Migration of implementation
   into those packages will be done incrementally. During migration we will
   keep the shim layer stable so downstream code doesn't break.

Consequences
------------
- Pros:
  - Stable public import surface for users and examples.
  - Clear separation of public API vs implementation, enabling parallel
    refactors (e.g., GPU adapters, headless vs windowed implementations).
  - Reduced import-time side-effects (lazy import of heavy deps).

- Cons / Risks:
  - During migration we must maintain compatibility between the shims and
    their backing implementation; this requires tests that exercise the
    shims end-to-end.
  - The shim layer adds a tiny indirection cost, but it's negligible for
    creative-coding use.

Implementation notes
--------------------

Shim behaviour
~~~~~~~~~~~~~~
- Provide `set_current_engine(engine)` and `get_current_engine()` helpers.
- Implement small shim functions: `size`, `background`, `rect`, `line`,
  `fill`, `stroke`, `stroke_weight`, `save_frame`, `frame_rate`, `no_loop`,
  `loop`, `redraw`, and utility `hsb_to_rgb`. Each shim attempts the
  following delegation strategy:
  1. Look for a direct attribute on the Engine or a known underscored
     internal (for example `size` -> `Engine._set_size`). If present, call it.
  2. Otherwise create a temporary `SimpleSketchAPI(engine)` and call the
     method there (this covers module-level functions and convenience
     bindings).
  3. If neither target is available raise an AttributeError — tests should
     detect and prompt mapping updates.

Package split and migration plan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We will migrate implementation into the new `src/core/*` packages in small,
test-backed steps. For each conceptual area (graphics, input, events, io,
shapes, image), follow this pattern:

1. Create package skeleton (already done).
2. Add a small pure-Python module that defines the minimal API and unit
   tests (interfaces only). For example `src/core/graphics/__init__.py`
   exposes `create_surface`, `draw_rect`, `snapshot` stubs.
3. Move the existing implementation code into the new package, adapting
   imports within the package and keeping the original public references
   (temporarily) for backwards compatibility.
4. Update tests to import from the public shim (`pycreative`) and assert
   behaviour. This provides high-level verification that the shim -> core
   mapping is correct.
5. Iterate: once the module is fully migrated and tests pass, remove the
   legacy implementation shim points.

Examples of concrete migration tasks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- graphics: move `GraphicsBuffer` and recording logic into `src/core/graphics`.
- engine: keep `Engine` as the orchestrator under `src/core/engine` and
  progressively move helper modules (api_registry, color, api, window)
  into `src/core/engine/` or `src/core/graphics` as appropriate.
- io: centralize snapshot backends (Pillow fallback, skia adapter) under
  `src/core/io/snapshot_backends.py` and provide a registration API so
  `Engine` can pick the best available backend at runtime.

Testing and CI
--------------
- Add smoke tests that import the public shims from `pycreative` and
  validate behaviour using the headless Engine (these are already in
  `tests/core/test_pycreative_shims.py`). Keep these tests fast and
  deterministic.
- Add integration tests for adapter-backed snapshotting (Skia/GL). Mark
  them as integration and skip in CI unless the environment supports the
  required binary wheels and GL context.

Migration checklist (short-term)
--------------------------------
1. Keep shims small and stable (done: `src/pycreative/__init__.py`).
2. Move pure helpers into `src/core/engine/` submodules (api_registry,
   graphics, color) — already performed as part of the earlier refactor.
3. Create `src/core/graphics` package and move GraphicsBuffer there.
4. Create `src/core/io` to host snapshot/backends and move `_save_frame`
   related helpers.
5. Add compatibility tests and expand the smoke tests to cover lifecycle
   APIs (setup/draw/no_loop/loop/redraw).

Follow-ups
----------
- Implement explicit mapping in the shim rather than heuristics: maintain
  a module-level dict of public name -> implementation target (preferred).
- Extract window and renderer logic into `src/core/engine/window.py` to
  isolate pyglet and GL imports.
- Implement the Skia adapter (`src/core/adapters/skia_gl.py`) and provide a
  runtime selection mechanism for snapshotting and rendering.
- Document the migration and a deprecation plan for any public API that
  must change.

Notes
-----
This ADR records the current plan and rationale. Treat it as a living
document: update the status to "Accepted" when the shims and package split
have full test coverage and the initial migration tasks complete.

``` 
