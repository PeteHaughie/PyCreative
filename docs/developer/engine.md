# Engine developer notes

This document explains the Engine responsibilities, public contract, and recommended TDD workflow for implementing engine features in PyCreative.

## Big picture

The Engine is the single event-loop authority for PyCreative. It owns:

- The main loop/lifecycle (`start`, `stop`).
- Wiring of public APIs and extensions via `register_api`.
- Surface and rendering context management (in collaboration with `src/core/graphics.py`).
- Input event propagation (`src/core/events.py`).

Keep the event loop centralized: do not implement competing loops in other modules.

## Public contract (minimal)

Implementations should offer at least the following public surface:

- `Engine()` — constructor (should be lightweight)
- `start()` — begin the engine loop (may be blocking for a full engine; tests can use no-op or thread-safe variants)
- `stop()` — stop the engine
- `register_api(api)` — register API objects, optionally calling `api.register(engine)` if present

The minimal test-suite-friendly stub in `src/core/engine.py` follows this contract.

## register_api conventions

- New API modules should expose a `register_api(engine)` function or a type with a `.register(engine)` instance method.
- The engine should store registered APIs for later use (e.g., in `engine.apis`).
- Prefer lazy initialization: only perform heavy work when the engine starts.

## TDD workflow (recommended)

Prefer Red → Green → Refactor:

1. Red: write a failing test that asserts the needed public contract or behaviour. Example: a test that instantiates `Engine` and checks `start`, `stop`, `register_api` exist.
2. Green: implement the minimal behaviour to make the test pass (small, well-tested stub is fine).
3. Refactor: improve the implementation, add more tests for edge cases, and expand functionality.

Example tests to start with:

- Lifecycle interface tests (existence of methods, flags like `running`).
- API registration tests (that `register_api` stores the API and calls a registration hook if present).
- Integration smoke tests that create an Engine, register a small fake API, start, then stop.

## Integration points

- `src/core/graphics.py` — surface creation and offscreen helpers. Use `create_graphics()` and `pixels()` context managers for pixel work.
- `src/api/` — public drawing/color APIs; these should register with the Engine when appropriate.
- `src/runner/cli.py` and `src/runner/loader.py` — how sketches are loaded and run by the Engine.

## Tests & CI

- The repository includes `tools/spec_validate_tests.py` which reads `specs/python-organisation-refactor/structure.yml` and validates that expected test file paths exist. Keep the expected paths present (they can be harmless placeholders) to satisfy spec validation.
- Tests live under `tests/`. Use pytest and follow project-level settings in `pyproject.toml`.

## Notes and best practices

- Do not block the Engine's main loop with long-running IO. Schedule via the Engine, or perform blocking work in background threads.
- Gate optional heavy deps behind try/except and list them in `[optional-dependencies]` in `pyproject.toml`.
- When in doubt about the public API, consult `docs/api/` and `specs/` for canonical contracts.

## Next steps

- Expand `tests/test_core.py` with more lifecycle and graphics tests.
- Add a small example under `examples/` showing Engine usage (this is useful for snapshot tests later).


