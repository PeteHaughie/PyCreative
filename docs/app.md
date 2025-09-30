# App / Sketch API

This page documents the high-level `Sketch` runtime and convenience helpers. It focuses on the APIs most commonly used by authors of sketches and small apps.

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

When invoked from the CLI (`pycreative examples/my_sketch.py`) the runner sets `sketch_path` automatically and will configure headless mode if requested.

## Running and headless mode

- `Sketch.run(max_frames=None)` — starts the pygame loop. Provide `max_frames` to stop after N frames. Useful for batch rendering or tests.
- Headless runs (useful for tests or rendering frames) are supported by the CLI which sets `SDL_VIDEODRIVER` before importing pygame. Example:

```bash
pycreative examples/my_sketch.py --headless --max-frames 1
```

## Window, frame, and basic helpers

- `size(w, h, fullscreen=False)` — set the sketch size (call in `setup`).
- `set_title(title)` — set window title.
- `set_double_buffer(True)` - Use the internal PyGame double buffer. Default is `True`.
- `set_vsync(1)` - Request vsync.
- `frame_rate(fps)` — request a target framerate; the run loop uses a `pygame.Clock` to throttle.
- `no_loop()` / `loop()` — runtime controls: `no_loop()` causes the runtime to draw once and stop; `loop()` resumes.

Sketch convenience properties (from the main surface):

- `width`, `height` — current window size
- `surface.size` — `(width,height)` tuple on the active `Surface` object

## Drawing state helpers and style context

Drawing state (fill/stroke/stroke_weight, caps/joins) is stored on the `Surface` wrapper (accessible at `self.surface`). The `Sketch` exposes thin shims to make common calls concise:

- `fill(color)` / `no_fill()`
- `stroke(color)` / `no_stroke()`
- `stroke_weight(w)`

Temporary style overrides are available as a context manager which mirrors Processing's push/pop style:

```py
with self.style(fill=(255,0,0), stroke=(0,0,0), stroke_weight=2):
    self.rect(10, 10, 100, 100)
# style restored automatically here
```

Additionally, all shape primitives accept per-call style keyword arguments. These override the current state for the single call and do not mutate the persistent surface style. Supported per-call keys include: `fill=`, `stroke=`, `stroke_weight=` (alias `stroke_width=` accepted).

Example:

```py
self.rect(10, 10, 100, 50, fill=(200, 20, 20), stroke=(0,255,0), stroke_weight=4)
```

## Primitives and helpers

Most drawing helpers are available directly on the Sketch and delegate to `self.surface`:

- `clear(color)` — clear the canvas.
- `rect(x,y,w,h, fill=None, stroke=None, stroke_weight=None)`
- `ellipse(x,y,w,h, fill=None, stroke=None, stroke_weight=None)`
- `line(x1,y1,x2,y2, stroke=None, width=None)`
- `point(x,y,color)`
- `image(img, x, y, w=None, h=None)` — draws or scales an image/OffscreenSurface.

Use `self.surface` directly when you need the Surface-level APIs (pixels, low-level blits, or style copying to offscreen surfaces).

## Offscreen drawing

Use `create_graphics(w, h, inherit_state=False)` to create an `OffscreenSurface`. When `inherit_state=True` the new offscreen buffer copies the current surface's drawing state (fill/stroke/stroke_weight) so common patterns (rendering text or shapes with the same style) are convenient.

`OffscreenSurface` behaves like the main surface and supports a context manager for scoped drawing:

```py
off = self.create_graphics(300, 200, inherit_state=True)
with off:
    off.clear((0,0,0))
    off.ellipse(150,100,100,100, fill=(255,128,0))

# draw to main surface
self.image(off, 20, 20)
```

See `docs/offscreen.md` for more patterns and caching helpers.

## Pixel access and image helpers

High level pixel APIs are summarized here; for full details and examples see `docs/pixels.md`.

- `with self.surface.pixels() as px:` — context manager providing a `PixelView` for read-modify-write pixel operations. The view hides numpy details and writes back on exit.
- `get_pixels()` / `set_pixels()` — copy-based helpers that return/accept array-like buffers.
- `load_image(path)` and `image(img, x, y, w=None, h=None)` — `load_image()` returns an `OffscreenSurface` or a Surface-like wrapper so images can be manipulated with the same API (pixels(), copy_to, blit).

## Saving snapshots and sequences

`Sketch.save_snapshot(path)` writes the current main surface to disk. Behavior:

- Relative paths are resolved next to the sketch file (`sketch_path`).
- Set `self.save_folder` in `setup()` to change where snapshots are written for that sketch.
- Support for sequential patterns: `{n}` and `###`-style placeholders for frame numbering are supported.

Example:

```py
self.save_snapshot('frames/frame_{n}.png')
```

## Debugging and testing tips

- For headless tests use the CLI `--headless` flag or set `SDL_VIDEODRIVER=dummy` before importing pygame.
- In tests, create small surfaces and inspect pixels after drawing to assert expected behavior.

## Where to look next

- `docs/pixels.md` — pixel API and PixelView usage.
- `docs/offscreen.md` — offscreen buffers, caching patterns, and examples.
- `src/pycreative/app.py` and `src/pycreative/graphics.py` — implementation of runtime and primitives.
