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
	- `Sketch.save_frame()` and `Sketch.save_folder` behaviour: frames are written next to the sketch by default and support sequence naming for animation frames. Check the Sketch API docs for the naming convention.

## Examples
The `examples/` directory includes runnable sketches that demonstrate the APIs. In particular:

- `examples/offscreen_example.py` — shows creating an offscreen buffer with `create_graphics`, drawing into it, using the `pixels()` context manager, and blitting the result back to the main surface.

Run examples with the CLI:
```bash
pycreative examples/offscreen_example.py
```

For more in-depth docs, see `docs/README.md` and the module-level docs under `src/pycreative/`.

## Why?

The reasoning behind building PyCreative was threefold: First, I had a problem to solve ie the need to have a lightweight fast portable framework for building interactive media devices, secondly as a method of learning GitHub's Spec Kit to see how AI assisted development works, and thirdly to see how large-scale python applications were made (although it's probably not a good example of that).

Processing and openFrameworks are both fantastic tools for creative coding—so why make another framework with a similar API? The short answer: portability and extensibility.

Processing is lightweight and fast to launch, but it isn’t well-suited for building hardware-driven projects like video synths. openFrameworks, on the other hand, is powerful and close to the metal, but it relies on complex toolchains (CMake, Make) or heavy IDEs (Xcode, Visual Studio) along with C++ addons, which can be a barrier for rapid experimentation.

After years of building projects with both frameworks, I wanted a middle ground: something with Processing’s simplicity, openFrameworks’ hardware potential, and Python’s flexibility. PyGame provides a fast, battle-tested engine for moving pixels around, but its quirks (like blitting) make it cumbersome for quick creative prototyping.

PyCreative hides those complexities behind a Processing-style API, while leveraging Python’s huge ecosystem. It runs out of the box on macOS, Windows, Linux, and even low-power devices like the Raspberry Pi—no complicated toolchain required. Add MIDI, OSC, GPIO, or whatever else you need through Python’s libraries, and you’ve got a powerful, extensible framework for creative coding and rapid prototyping.

More information is in the [docs/README.md](docs/README.md)

## Directory Structure
- [src/pycreative/](src/pycreative/): Main source code
- [docs/](docs/): Class documentation
- [examples/](examples/): Example sketches
- [sketches/](sketches/): User sketches
- [tests/](tests/): Test suite

## License
MIT
