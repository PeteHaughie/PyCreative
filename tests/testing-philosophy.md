Testing philosophy and rules for contributors

This file documents the testing conventions for the PyCreative project. It is
intended to be concise and actionable so maintainers and contributors follow a
consistent approach.

Core rules
- Minimize import-time side-effects. Core modules must not import heavy
  native deps (skia, pygame) at import time. Use adapter modules under
  `src/core/adapters/` and perform lazy imports inside those adapters.
- Prefer dependency injection over monkeypatching. Tests should inject fake
  adapters or use fixtures rather than modifying global imports unless the
  test is specifically a Red test that simulates the dependency being missing.
- Centralize monkeypatching. If a test must alter sys.modules, use the
  `no_skia` or `isolated_monkeypatch` fixtures (see `tests/conftest.py`).
- Snapshot tests should prefer draw-call sequence assertions rather than
  pixel-perfect image diffs. Use a FakeRenderer that records `.calls`.

Monkeypatching rules
- Allow monkeypatching of external dependencies only in explicitly marked
  tests (e.g. early Red tests). For other tests, prefer DI or fixtures.
- Tests that use module-level monkeypatching should be marked with
  `@pytest.mark.isolation` to avoid parallel test interference.

Renderer vs Adapter responsibilities
- Renderer: small, dumb dispatcher that maps descriptor types to adapter
  draw calls. It should not implement drawing algorithms (no geometry math).
- Adapter: contains platform-specific drawing logic and integration with
  native libraries. For example, `skia_adapter.draw_circle(...)` contains the
  Skia-specific code to draw a circle.

Ownership & surface wiring
- The adapter that creates a surface owns the surface lifecycle unless
  explicitly transferred. `attach_skia_to_pygame` must document who owns
  the returned surface and whether it mutates the input pygame surface.

Testing helpers
- Provide small fakes (e.g., FakeRenderer) to assert call sequences. Add these
  helpers near tests or under `tests/support/` when reused across files.
