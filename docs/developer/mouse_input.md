## Mouse input integration (developer notes)

This document explains how mouse input is integrated into the headless
Engine used for tests and development. It documents the lightweight
pyglet adapter, the Engine simulation helpers, the sketch handler
contracts, pmouse semantics, and testing guidance.

These internals are intentionally small and test-friendly: we accept
duck-typed event objects (so tests don't need pyglet) and provide a
tiny adapter that maps pyglet constants when available.

### Design goals

- Keep headless tests independent from a real `pyglet` runtime.
- Provide a stable, minimal API for simulating input in tests.
- Accept either primitive arguments (x, y, button) or duck-typed
  event objects (attributes `.x`, `.y`, `.button`, and `.get_count()`)
  so callers can pass simple fakes.
- Expose a small set of `Engine.simulate_mouse_*` helpers for tests to
  exercise event dispatch and engine state changes.

### Files touched / implementation locations

- Engine simulation helpers: `src/core/engine/impl.py` (methods added: `simulate_mouse_press`, `simulate_mouse_release`, `simulate_mouse_move`, `simulate_mouse_drag`, `simulate_mouse_wheel`).
- Pyglet adapter (lazy): `src/core/adapters/pyglet_mouse.py` (helpers: `normalize_button`, `normalize_event`).
- Tests updated to use the helpers: `tests/core/test_mouse_input.py`.

### Adapter behavior

`src/core/adapters/pyglet_mouse.py` is intentionally tiny and lazy-loads
`pyglet` only when available. It provides two helpers:

- `normalize_button(py_button) -> Optional[str]`
  - Maps pyglet mouse constants to the strings `'LEFT'`, `'RIGHT'`, `'CENTER'` when pyglet is available.
  - Returns `None` when pyglet is not present or mapping failed.

- `normalize_event(event) -> dict`
  - Accepts either a mapping (dict) or a duck-typed object and returns a
    plain dict with keys like `x`, `y`, `button` and possibly
    `get_count` (a callable for wheel events).
  - This makes it cheap for Engine helpers to accept either real
    pyglet event objects or small fake objects used in tests.

The adapter never forces `pyglet` to be imported at module import time;
tests and CI remain pyglet-free unless windowed mode is used.

### Engine simulation helpers (API contract)

The Engine exposes the following helper methods for tests:

- `simulate_mouse_press(x: Optional[int]=None, y: Optional[int]=None, button: Optional[str]=None, event: Optional[object]=None)`
  - Ensures `setup()` has run (calls a single headless frame if needed).
  - Updates pmouse/mouse values, sets `mouse_pressed = True` and
    `mouse_button` accordingly, then dispatches `sketch.mouse_pressed()`
    if present.

- `simulate_mouse_release(x: Optional[int]=None, y: Optional[int]=None, button: Optional[str]=None, event: Optional[object]=None)`
  - Ensures `setup()` has run, updates state, sets `mouse_pressed = False`, calls `mouse_released()` and then `mouse_clicked()` (if present).

- `simulate_mouse_move(x: Optional[int]=None, y: Optional[int]=None, event: Optional[object]=None)`
  - Updates pmouse/mouse and calls `mouse_moved()` if present. Does not alter `mouse_pressed`.

- `simulate_mouse_drag(x: Optional[int]=None, y: Optional[int]=None, button: Optional[str]=None, event: Optional[object]=None)`
  - Ensures `mouse_pressed` is `True`, updates coords, and calls `mouse_dragged()`.

- `simulate_mouse_wheel(event_or_count: object)`
  - Accepts either an event-like object with `.get_count()` or a numeric
    count; calls `mouse_wheel(event)` on the sketch if present. A small
    wheel-shim object is created and passed to the handler to provide
    a consistent `get_count()` interface.

Notes about calling convention
- The Engine prefers to call sketch handlers with a `SimpleSketchAPI(this)`-like
  helper when a handler expects a `this` argument. The engine uses
  `_call_sketch_method()` which attempts `fn(this)` and falls back to `fn()` on TypeError.

### Sketch handler contracts

Sketch authors should implement zero-argument handlers OR handlers that accept the `this` convenience object provided by the engine. The following handlers are recognized and will be called by the Engine when simulated:

- `mouse_pressed()` — called when a press is simulated (or real press in windowed mode).
- `mouse_released()` — called on release.
- `mouse_clicked()` — called after release (press+release semantics).
- `mouse_moved()` — called when the pointer moves and no button is pressed.
- `mouse_dragged()` — called when pointer moves while a button is pressed.
- `mouse_wheel(event)` — event should expose `.get_count()`.

Handlers may be either module-level functions or class-bound methods on
`Sketch` instances; the Engine's `_call_sketch_method` handles both
forms.

### pmouse semantics

- `pmouse_x` and `pmouse_y` are set to the previous values of `mouse_x` and `mouse_y` before applying the new coordinates when simulating an event. This mirrors the typical "previous-frame" semantics used in PyCreative-style APIs.
- When simulating events directly (without drawing frames), the Engine updates `pmouse` before updating current coords so handlers can compare the previous and current positions.

### Lifecycle notes

- The Engine runs `setup()` before dispatching any simulated events if
  it hasn't already. The helper `simulate_mouse_*` calls `_ensure_setup()`
  which runs a single headless frame to execute `setup()` and capture any
  setup commands.
- This keeps test behavior consistent with the docs: event handlers are
  invoked only once the sketch lifecycle (setup/draw) is active.

### Error handling and test behaviour

- Simulation helpers are defensive: they catch exceptions raised by user
  handlers to avoid crashing test harnesses. This is intentional for
  early development; if you prefer tests to fail loudly when handler code
  raises, change the helper to re-raise the exception instead of
  swallowing it.

### Testing guidance

- Prefer the Engine simulation helpers in unit tests. They centralize
  lifecycle handling and ensure `pmouse` semantics are applied
  consistently.
- For wheel tests, provide a tiny fake object with `get_count()` (the
  tests use a `FakeEvent` class) or pass an integer directly to
  `simulate_mouse_wheel()`.
- If you need to assert that `setup()` ran, call `eng.run_frames(1)` or
  rely on the simulation helpers (they call `_ensure_setup()` for you).

### Follow-ups and TODOs

- Consider exposing test-only convenience methods on `SimpleSketchAPI` so
  sketches themselves can simulate input in integration-style tests.
- Optionally change exception policy in simulate helpers to re-raise
  user exceptions (so tests fail fast on bad handler code).
- Add a short cross-reference entry in `docs/api/input/mouse/` describing
  the testing helpers (for end-users writing tests). This can be a
  small note linking to `docs/developer/mouse_input.md`.

