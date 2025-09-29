# App / Sketch API

This page documents the high-level `Sketch` runtime and convenience helpers that make writing sketches concise and idiomatic.

## Overview

A `Sketch` is the main application object. Subclass `Sketch` and override lifecycle hooks:

- `setup(self)` — called once before the run loop; use to call `size()` and initialize state.
- `update(self, dt)` — called each frame before `draw()` with the elapsed time (seconds).
- `draw(self)` — called each frame to render. Use drawing helpers on `self` or `self.surface`.
- `on_event(self, event)` — low-level input event hook.
- `teardown(self)` — called during shutdown for cleanup.

Run a sketch with:

```py
if __name__ == '__main__':
    MySketch(sketch_path=__file__).run()
```

When invoked from the CLI (`pycreative examples/my_sketch.py`) the runner sets `sketch_path` automatically.

## Running and headless mode

- `Sketch.run(max_frames=None)` — starts the pygame loop. Provide `max_frames` to stop after N frames.
- Headless runs (useful for tests or rendering frames) should be invoked via the CLI which sets `SDL_VIDEODRIVER` early. Example:

```bash
pycreative examples/my_sketch.py --headless --max-frames 1
```

## Window and frame helpers

- `size(w, h, fullscreen=False)` — set the sketch size (call in `setup`).
- `set_title(title)` — set window title.
- `frame_rate(fps)` — request a framerate; the run loop will throttle using pygame.Clock.
- `no_loop()` / runtime `no-loop` mode — use `self.no_loop()` to draw once and stop updating.

## Drawing state helpers

State is managed on `self.surface` (a `Surface` wrapper). The `Sketch` provides thin convenience shims that forward to the surface:

- `fill(color)` / `no_fill()`
- `stroke(color)` / `no_stroke()`
- `stroke_weight(w)`

Per-call overrides are also accepted by high-level primitives; for example `self.rect(x,y,w,h, fill=(r,g,b))` will apply the fill for that call only.

## Primitives and helpers

Common helpers available on the Sketch or on `self.surface`:

- `clear(color)` — clear the canvas.
- `rect(x,y,w,h, fill=None, stroke=None, stroke_weight=None)`
- `ellipse(x,y,w,h, fill=None, stroke=None, stroke_weight=None)`
- `line(x1,y1,x2,y2, color=None, width=None)`
- `point(x,y,color)`
- `image(img, x, y, w=None, h=None)` — draws or scales an image.
- `bezier(...)`, `bezier_detail(steps)` — cubic bezier helpers.
- `curve(...)`, `curve_detail(steps)`, `curve_tightness(t)` — curve helpers.

If you need an offscreen buffer, use `create_graphics(w,h, inherit_state=False)` which returns an `OffscreenSurface` with the same API as `self.surface`.

## Convenience: save snapshots and sequences

`Sketch.save_snapshot(path)` writes the current main surface to disk. Behavior:

- If `path` is relative it is resolved next to the sketch file (the directory of `sketch_path`) so examples that call `self.save_snapshot('out.png')` save beside the sketch.
- Prefer a per-sketch setting: set `self.save_folder = 'snapshots'` in `setup()` or call
    `self.set_save_folder('snapshots')`. This value is used in preference to the
    environment variable if present. Example:

```py
def setup(self):
        self.save_folder = 'snapshots'   # or: self.set_save_folder('snapshots')
```

If you don't set a per-sketch folder, `PYCREATIVE_SNAP_DIR` remains a supported
fallback and may point to a directory relative to the sketch file.

- Sequential numbering is supported using placeholders:
  - `{n}` — replaced with the next integer (1,2,3...).
  - `###` (1-6 `#`) — replaced with a zero-padded integer with width equal to number of `#`.

Examples:

```py
self.save_snapshot('frame_{n}.png')    # frame_1.png, frame_2.png, ...
self.save_snapshot('frame_####.png')   # frame_0001.png, frame_0002.png
```

Processing note: Processing's `saveFrame()` uses `####`-style placeholders. We support a similar pattern plus `{n}` which is easier to generate programmatically.

## Pixel access and image helpers

For full guidance on pixel access and the `PixelView` object returned by `get_pixels()`, see `docs/pixels.md`.

Short summary:

- `get_pixels()` returns a `PixelView` (shape `(H,W,C)`) that wraps a numpy array when available or a nested list fallback.
- `set_pixels(arr)` writes the array back to the surface (accepts `PixelView` as well).
- Use `self.surface.is_numpy_backed()` to detect whether you can operate on a numpy ndarray (lazy import of numpy recommended).

## CLI and examples

Use the `pycreative` CLI to run sketches, set headless mode, and limit frames. The CLI ensures `SDL_VIDEODRIVER` is set before importing pygame for headless use.

Example basic sketch:

```py
from pycreative.app import Sketch

class MySketch(Sketch):
    def setup(self):
        self.size(320, 240)
    def draw(self):
        self.clear((0,0,0))
        self.ellipse(self.width/2, self.height/2, 100, 100, fill=(200,20,20))

if __name__ == '__main__':
    MySketch().run()
```

## Where to look next

- `docs/pixels.md` — pixel API and PixelView usage.
- `examples/` — runnable sketches demonstrating features.
- `src/pycreative/app.py` and `src/pycreative/graphics.py` — source for runtime and drawing primitives.

If you want, I can add a small `docs/usage.md` with quick recipes (record a frame sequence, render offscreen buffers, headless CI tips). Which recipes would be most helpful? 
