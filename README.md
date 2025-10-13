# PyCreative

[![CI](https://github.com/PeteHaughie/PyCreative/actions/workflows/ci.yml/badge.svg)](https://github.com/PeteHaughie/PyCreative/actions/workflows/ci.yml)


PyCreative is a batteries-included creative-coding framework that makes it trivial to build visual, audio, and interactive projects in Python while staying lightweight and extensible. It uses Pyglet for low-level drawing, input, and window/context management, but provides higher-level conveniences: a component-driven app loop, scene & state management, easy shader support, multimedia I/O, asset management, utilities for math & noise, tight integration for live-coding, and idiomatic Python APIs inspired by Processing and openFrameworks.

## Features
- Modular architecture for easy extension
- 2D/3D graphics, OpenGL, audio, video, MIDI, user input
- Asset management, hot-reload, and live-coding support
- Simple, discoverable, and chainable APIs

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

After years of building projects with both frameworks, I wanted a middle ground: something with Processing’s simplicity, openFrameworks’ hardware potential, and Python’s flexibility. Pyglet provides a fast, battle-tested engine for moving pixels around, but its quirks (like blitting) make it cumbersome for quick creative prototyping.

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
