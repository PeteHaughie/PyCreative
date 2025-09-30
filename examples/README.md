# Examples directory

This folder contains small sketches and example scripts showing how to use the
pycreative API. These files are intended as documentation and demonstration
code rather than part of the automated unit test surface.

Conventions
-----------
- Top-level example sketches should be named with the `_example.py` suffix
  (for example `bouncing_balls_class_example.py`). This makes it obvious which
  files are runnable examples and helps tooling filter them.
- If you need reusable helpers (small classes, utilities, or data used by
  multiple examples), put them into `examples/_helpers/` so they won't be
  mistaken for a standalone example.

Why examples are skipped by tests
---------------------------------
Examples are educational artifacts and often include local imports, ad-hoc
helpers, or interactive code that's not suitable for CI unit tests. To avoid
spurious failures in the project's test suite, example checks are skipped by
default in CI and during regular `pytest` runs.

Running examples
----------------
To run an example script directly:

```bash
python examples/sketch_example.py
```

Or, if you prefer the package entrypoint, you can run with:

```bash
python -m pycreative examples/sketch_example.py
```

Of if it is installed already:
```bash
pycreative examples/sketch_example.py
```

Notes
-----
- Keep examples small and self-contained.

# Examples

This folder contains example sketches demonstrating PyCreative features.

- `offscreen_example.py` — demonstrates creating an offscreen buffer with `create_graphics()`, rendering an expensive static pattern into it once, and blitting the cached buffer each frame.
- `polyline_caps_mitres_example.py` — demonstrates polyline drawing and the current cap/join emulation behavior (round caps/joins stamped).
- `graphics_example.py`, `input_example.py`, etc. — other examples illustrating the runtime and APIs.
- `bezier_example.py` — shows drawing cubic bezier curves and how to adjust bezier detail.
- `bouncing_ball_example.py` — simple procedural bouncing ball demo (single ball).
- `bouncing_balls_class_example.py` — class-based bouncing balls demo (uses a Ball helper class).
- `copy_example.py` — demonstrates pixel/image copy and basic surface operations.
- `curve_example.py` — demonstrates Processing-style curve primitives.
- `graphics_example.py` — general graphics primitives and usage of the Surface API.
- `input_example.py` — shows keyboard and mouse handling with the Sketch input simplifications.
- `offscreen_example.py` — demonstrates creating an offscreen buffer with `create_graphics()`, rendering an expensive static pattern into it once, and blitting the cached buffer each frame.
- `offscreen_transformations_example.py` — demonstrates drawing into offscreen surfaces while sharing or inheriting transforms.
- `pixels_example.py` — demonstrates pixel-level access and copying between images.
- `pixels_image_copy_example.py` — another pixels/image copy focused example.
- `polyline_caps_mitres_example.py` — demonstrates polyline drawing and the current cap/join emulation behavior (round caps/joins stamped).
- `save_snapshot_example.py` — demonstrates `save_snapshot()` and filename sequencing.
- `shape_example.py` — example showing higher-level shape helpers and polygon drawing.
- `sketch-lifecycle_example.py` — demonstrates Sketch lifecycle hooks and no-loop behavior.
- `sketch_example.py` — minimal example sketch showing the smallest runnable sketch.
- `style_override_example.py` — shows per-call style overrides and the `style()` context manager.
- `transforms_example.py` — shows the transform stack (push/pop/translate/rotate/scale) and how primitives are affected.
