# PyCreative

PyCreative is a batteries-included creative-coding framework that makes it trivial to build visual, audio, and interactive projects in Python while staying lightweight and extensible. It uses PyGame for low-level drawing, input, and window/context management, but provides higher-level conveniences: a component-driven app loop, scene & state management, easy shader support, multimedia I/O, asset management, utilities for math & noise, tight integration for live-coding, and idiomatic Python APIs inspired by Processing and openFrameworks.

A batteries-included creative coding framework for Python, inspired by Processing/openFrameworks, built atop PyGame.

## Features
- Modular architecture for easy extension
- 2D/3D graphics, OpenGL, audio, video, MIDI, user input
- Asset management, hot-reload, and live-coding support
- Simple, discoverable, and chainable APIs

## What's new (API highlights)
This repository includes several recent API improvements inspired by Processing-style workflows and convenience wrappers around Pygame. Key additions:

- Pixel access (PImage-style)
	- Use the `pixels()` context manager on any `Surface` to get/set pixel data without directly exposing numpy. The returned object behaves like a simple 2D pixel view and will write back on exit.
	- Example:
		```python
		with surface.pixels() as px:
				px[10,10] = (255,0,0,255)  # RGBA tuple
		```

- Offscreen drawing / PGraphics
	- `OffscreenSurface` provides a lightweight, context-manageable offscreen buffer. Use `Sketch.create_graphics(width, height, inherit_state=True)` to create an offscreen surface that can inherit drawing state (fill, stroke, stroke_weight) from the main sketch.
	- Offscreen surfaces can be drawn onto the main surface with `blit_image` / `blit` helpers or via `Surface.blit()`.

- Per-call style overrides for primitives
	- All shape primitives support per-call style keyword arguments: `fill=`, `stroke=`, `stroke_weight=` (alias `stroke_width=` supported). These override the surface's current style for that single call.
	- Example:
		```python
		surface.rect(10,10,100,100, fill=(255,0,0), stroke=(0,255,0), stroke_weight=4)
		```

- Sketch image and load helpers
	- `Sketch.load_image(path)` returns an `OffscreenSurface` (or a Surface-like wrapper) so images are easy to manipulate with the same API (pixels, copy, blit).
	- `Sketch.image(img, x, y, w=None, h=None)` accepts either a Pygame Surface or an OffscreenSurface and will extract the raw surface when needed.

- Style context manager
	- Use `with sketch.style(fill=(...), stroke=(...), stroke_weight=...)` to temporarily override drawing state inside a scoped block. This mirrors Processing's `pushStyle()` / `popStyle()` in an idiomatic Python context manager.

- Convenience and compat
	- `Surface.size` property returns (width, height) for quick access.
	- `Surface.img()` alias exists for image-like helpers.
	- `Sketch.save_snapshot()` and `Sketch.save_folder` behaviour: snapshots are written next to the sketch by default and support sequence naming for animation frames. Check the Sketch API docs for the naming convention.

## Examples
The `examples/` directory includes runnable sketches that demonstrate the APIs. In particular:

- `examples/offscreen_example.py` — shows creating an offscreen buffer with `create_graphics`, drawing into it, using the `pixels()` context manager, and blitting the result back to the main surface.

Run examples with the CLI:
```bash
pycreative examples/offscreen_example.py
```

For more in-depth docs, see `docs/README.md` and the module-level docs under `src/pycreative/`.

## Why?
When Processing and openFrameworks already exist why bother making *another* creative coding framework with the same API? I love both Processing and openFrameworks but they both come with some pretty serious caveats to the end user. Processing is simple to use and is fast to launch but it is not suitable for building hardware devices like video synths. openFrameworks is close to the tin and very suitable for hardware devices but it also comes with a heavy dependency on complicated toolchains like cmake and make or IDEs like Xcode and Visual Studio Code and C++ addons to extend from the base application. I've built many many art projects and tools with both frameworks and love them dearly. So then why build it again? Portability and extensibility. PyGame is a highly optimised game engine designed for moving things around a canvas quickly. However it also has its own idiosyncratic quirks such as blitting which are not easy to tame when you're just trying to build a prototype shape generator for a gallery for example. With a few well maintained and tested libraries under the hood hidden behind the Processing idiomatic API it becomes a very capable framework for rapid prototyping and creative coding - yet another tool in the toolbox with a familiar API suitable for low power devices such as the Raspberry Pi or even on higher end hardware across Mac OS, Windows, and Linux - all out of the box with no complicated toolchain and able to make the most from the wide world of Python libraries that already exist for intigration with MIDI, OSC, GPIO etc.

## Quickstart
```bash
pycreative examples/hello_sketch.py
```

More information is in the [docs/README.md](docs/README.md)

## Directory Structure
- [src/pycreative/](src/pycreative/): Main source code
- [docs/](docs/): Class documentation
- [examples/](examples/): Example sketches
- [sketches/](sketches/): User sketches
- [tests/](tests/): Test suite

## License
MIT
