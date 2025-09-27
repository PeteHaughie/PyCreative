# PyCreative

PyCreative is a batteries-included creative-coding framework that makes it trivial to build visual, audio, and interactive projects in Python while staying lightweight and extensible. It uses PyGame for low-level drawing, input, and window/context management, but provides higher-level conveniences: a component-driven app loop, scene & state management, easy shader support, multimedia I/O, asset management, utilities for math & noise, tight integration for live-coding, and idiomatic Python APIs inspired by Processing and openFrameworks.

A batteries-included creative coding framework for Python, inspired by Processing/openFrameworks, built atop PyGame.

## Features
- Modular architecture for easy extension
- 2D/3D graphics, OpenGL, audio, video, MIDI, user input
- Asset management, hot-reload, and live-coding support
- Simple, discoverable, and chainable APIs

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
