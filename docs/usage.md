# Usage recipes

Practical recipes and short examples to get started quickly with `Sketch` and the
high-level helpers in PyCreative.

## Quick start

Create a sketch by subclassing `Sketch`. Call `size()` in `setup()` and draw in
`draw()`:

```py
from pycreative.app import Sketch

class HelloSketch(Sketch):
    def setup(self):
        self.size(640, 480)

    def draw(self):
        self.clear((30, 30, 40))
        self.ellipse(self.width/2, self.height/2, 200, 200, fill=(200,100,40))

if __name__ == '__main__':
    HelloSketch(sketch_path=__file__).run()
```

Run from the command line with the `pycreative` CLI to enable headless options and
other conveniences.

## Running headless (CI-friendly frame capture)

The CLI sets SDL environment variables early so `pygame` can initialize in
headless/dummy mode. Use `--headless` and `--max-frames` to render a small
sequence and exit (good for CI snapshots):

```bash
pycreative examples/my_sketch.py --headless --max-frames 1
```

If you need to run the script directly (without the CLI), set the environment
before importing pygame:

```bash
export SDL_VIDEODRIVER=dummy
python examples/my_sketch.py
```

On macOS in CI you may prefer to use a macOS-specific headless strategy (the
CLI already handles common cases).

## Save snapshots and sequences

Use `self.save_frame(path)` inside your sketch to write the current frame to
disk. Recommended patterns:

- Per-sketch folder (preferred):

```py
def setup(self):
    self.save_folder = 'snapshots'   # preferred: per-sketch setting

def draw(self):
    # produce a frame and save it
  self.save_frame('frame_{n}.png')
```

- Property or method are both supported:

```py
self.save_folder = 'shots'
# or
self.set_save_folder('shots')
```

- Placeholders are supported for sequences:
  - `{n}` yields sequential integers (1,2,3...) and
  - `####` / `##` etc. create zero-padded numbers.

Examples:

```py
self.save_frame('frame_{n}.png')    # frame_1.png, frame_2.png, ...
self.save_frame('frame_####.png')   # frame_0001.png, frame_0002.png
```

If no per-sketch folder is set, the `PYCREATIVE_SNAP_DIR` environment variable
is used as a fallback; if neither is present snapshots are written beside the
sketch file.

## Pixel access (PixelView) and lazy numpy

`Surface.get_pixels()` returns a `PixelView` that wraps either a numpy
ndarray (when available) or a nested-list fallback, and `Surface.set_pixels()`
accepts the same wrapper.

Best practice: keep numpy imports inside `setup()` or `draw()` so examples and
tests remain import-safe (no heavy imports at module import time):

```py
def draw(self):
    pv = self.surface.get_pixels()  # PixelView
    # If numpy is available and you need it, import lazily
    if self.surface.is_numpy_backed():
        import numpy as np

        arr = pv.raw()  # returns the ndarray
        # vectorized ops here
        arr[..., 0] = np.clip(arr[..., 0] + 10, 0, 255)
        self.surface.set_pixels(arr)
    else:
        # safe Python fallback using PixelView indexing
        h, w, c = pv.shape
        for y in range(h):
            for x in range(w):
                r, g, b = pv[y, x]
                pv[y, x] = (min(255, r + 10), g, b)
        self.surface.set_pixels(pv)
```

Notes:
- `pv.raw()` returns the underlying object (ndarray or nested lists).
- `PixelView` implements shape and indexing so small sketches don't need numpy
  everywhere.

## Offscreen rendering (create_graphics)

Create an offscreen surface for intermediate rendering, then draw it to the
main surface:

```py
g = self.create_graphics(320, 240)
g.clear((0,0,0))
g.ellipse(160,120,100,100, fill=(255,0,0))
# draw offscreen onto main surface
self.surface.blit_image(g.raw, 10, 10)
```

`create_graphics()` returns an object compatible with the same drawing API as
`self.surface`. Use `inherit_state=True` to copy fill/stroke state from the
main surface if you need matching styles.

## Shape construction modes (begin_shape)

`Surface` and `Sketch` expose a Processing-like shape construction API using:

- `begin_shape(mode=None)` — start collecting vertices. `mode` may be one of:
  `POINTS`, `LINES`, `TRIANGLES`, `TRIANGLE_FAN`, `TRIANGLE_STRIP`, `QUADS`,
  or `QUAD_STRIP`. Omit `mode` to build an arbitrary polygon/polyline.
- `vertex(x,y)` — add a vertex.
- `bezier_vertex(cx1,cy1,cx2,cy2,x3,y3)` — add a cubic bezier segment attached
  to the previous vertex; flattened at draw time.
- `end_shape(close=False)` — finish and draw. `close=True` will close the
  polygon when applicable.

Example (in a `Sketch`):

```py
def draw(self):
    self.clear((10, 10, 10))
    self.fill((255, 200, 100))
    self.begin_shape('QUADS')
    self.vertex(10, 10)
    self.vertex(90, 10)
    self.vertex(90, 70)
    self.vertex(10, 70)
    self.end_shape()
```

## CI and tests: quick recipe

1. Add a tiny headless run in CI that renders a few frames and asserts that
   output files exist.

2. Use `--max-frames` for deterministic runs and side-effect outputs:

```bash
pycreative examples/save_snapshot_example.py --headless --max-frames 2
# then assert files exist in the snapshots folder
```

3. Keep numpy imports lazy (inside build/draw) so tests can import modules
   without requiring a display driver or numpy at import time.

## Troubleshooting

- If `save_snapshot()` fails to write files, check permissions and ensure the
  per-sketch `save_folder` is not pointing at an invalid location. You can set
  `self.save_folder = None` to clear it and fall back to the environment or
  sketch directory.
- For headless runs, prefer the CLI which sets `SDL_VIDEODRIVER` for you. If
  you run the script directly, set `SDL_VIDEODRIVER=dummy` before importing
  pygame.
