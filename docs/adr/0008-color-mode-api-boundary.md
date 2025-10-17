# ADR 0008: Normalize color modes at the Engine API boundary

Status: Accepted

Context
-------
Sketch authors expect multiple convenient color modes (notably RGB and HSB).
Rendering primitives, presenters and adapters operate most efficiently when
they receive a simple, canonical RGBA representation. Allowing low-level
renderers to accept multiple modes would increase complexity across the
rendering stack and risk inconsistencies between windowed and headless
presentations.

Decision
--------
Normalize color modes at the Engine API boundary: provide `this.color_mode()`
on the Sketch API and have high-level helpers (`this.fill`, `this.stroke`,
`this.background`) convert user inputs from the selected color mode into a
canonical RGBA representation before passing them to the engine's recording
and presenter layers.

Rationale
---------
- Simplicity: downstream rendering code (presenters/adapters) can assume a
  fixed format (RGBA integer tuples or packed ints). This reduces the number
  of code paths and potential bugs.
- Testability: pure color conversion functions (e.g., `hsb_to_rgb`,
  `rgb_to_hsb`) are easy to unit test in isolation and do not require engine
  setup.
- Extensibility: adding new modes (LAB, CMYK, etc.) becomes a local change
  in core/color and API parsing modules rather than a cross-cutting change
  across presenters and adapters.
- Performance: conversion happens once at the API boundary; the renderer
  receives ready-to-use RGBA values with no per-primitive branching.

Consequences
------------
- The Engine records colors as canonical RGBA values; presenters expect RGBA.
- The pure helper `core.color.color()` remains engine-agnostic and continues
  to return packed ARGB integers. Sketch authors should prefer `this.fill`
  and similar when they want mode-aware behaviour.
- Tests should validate both the pure conversion helpers and the
  integration where `this.color_mode()` influences recorded drawing commands.

Alternatives considered
-----------------------
- Letting presenters accept multiple color formats: rejected due to increased
  complexity and test surface area.
- Making `color()` engine-aware by default: rejected because `color()` is
  used in contexts where no engine is available (pure tests, utility code).

Implementation notes
--------------------
- Implemented `SimpleSketchAPI.color_mode(mode)` to normalize and store the
  canonical mode on the engine (`'RGB'` or `'HSB'`).
- `src/core/color/fill.py`, `stroke.py` and `background.py` consult
  `engine.color_mode` and call `hsb_to_rgb` when appropriate.
- Added pure helper `rgb_to_hsb` for symmetry and tests.

"""

