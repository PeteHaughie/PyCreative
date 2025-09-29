# Examples

This folder contains example sketches demonstrating PyCreative features.

- `offscreen_example.py` — demonstrates creating an offscreen buffer with `create_graphics()`, rendering an expensive static pattern into it once, and blitting the cached buffer each frame.
- `polyline_caps_mitres_example.py` — demonstrates polyline drawing and the current cap/join emulation behavior (round caps/joins stamped).
- `graphics_example.py`, `input_example.py`, etc. — other examples illustrating the runtime and APIs.

Run an example:

```bash
python -m pycreative.cli examples/offscreen_example.py --max-frames 60
```

Notes

- Examples prefer a visible display; use `--headless` when running in CI or when no display is available.
- For development, run `pytest` to run unit tests covering core behaviors.
