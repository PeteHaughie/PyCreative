---
title: Engine color_mode (developer guide)
---

This page documents the engine-level color mode support used by sketches and
the internal design that normalizes user-provided color inputs at the API
boundary.

Why this exists
---------------
Sketch authors expect convenient color modes (RGB, HSB). The engine exposes
`this.color_mode(...)` as a lightweight API so sketches can switch modes at
runtime. Conversions from alternate color spaces are done at the API
boundary (before drawing primitives receive values) so low-level rendering
paths remain fast and only consume RGBA values.

Key concepts
------------
- color_mode: an engine-level string stored on `engine.color_mode` (canonical
  values: `'RGB'`, `'HSB'`). Sketches call `this.color_mode('HSB')` to change
  mode for subsequent color-setting calls (fill/stroke/background).
- API boundary normalization: high-level helpers (`this.fill`, `this.stroke`,
  `this.background`) parse user arguments and convert them into canonical
  RGBA forms (integer 0..255 for RGB channels; alpha normalized to 0..1 where
  appropriate). This keeps the renderer and presenters free from
  multi-mode branching.
- Pure conversion helpers live in `src/core/color` (for example:
  `hsb_to_rgb`, `rgb_to_hsb`) so they are easy to test in isolation.

How to use from a sketch
-------------------------
Example (HSB background + fill):

```py
def setup(this):
    this.color_mode('HSB')
    # HSB: hue in 0..1 or 0..255, saturation/value in 0..1 or 0..255
    this.background(0.0, 1.0, 1.0)  # bright red
    this.fill(0.0, 1.0, 1.0)        # bright red fill
```

Notes for authors
-----------------
- The engine converts HSB inputs into RGB via `hsb_to_rgb` before storing
  the color on `engine.fill_color` / `engine.stroke_color` / recording the
  `background` command. Look at `src/core/color/fill.py` / `stroke.py` /
  `background.py` for the exact parsing behaviour.
- The top-level pure helper `core.color.color()` is intentionally pure and
  independent of the engine. It accepts floats in 0..1 or ints in 0..255 and
  returns a packed ARGB integer. Use `this.fill(...)` for engine-aware
  behaviour in sketches.

Extending with new modes
------------------------
To add a new color mode (for example, a `LAB` mode) prefer the following
pattern:

1. Implement pure conversion helpers in `src/core/color/` (e.g.,
   `lab_to_rgb` and `rgb_to_lab`). Keep these functions pure and well-tested.
2. Update the API method `SimpleSketchAPI.color_mode` to accept a new alias
   and store a canonical string on `engine.color_mode`.
3. Update `src/core/color/fill.py`, `stroke.py` and `background.py` to handle
   the new `engine.color_mode` via a small mapping or switch that calls the
   new converter when needed.

Testing guidance
----------------
- Unit test pure conversion functions (round-trip tests, edge cases).
- Add integration tests that exercise `this.color_mode(...)` followed by
  `this.fill(...)`, `this.stroke(...)` and `this.background(...)`. The
  project's headless `Engine` records these operations in `engine.graphics`
  so tests can assert the recorded RGB values.

Migration notes
---------------
Existing sketches that call `color()` directly are unaffected. If you want
them to respect an engine `color_mode`, update the sketch to call the
engine-aware methods (`this.fill`, etc.), or adjust your helpers to use the
engine's mode explicitly.
