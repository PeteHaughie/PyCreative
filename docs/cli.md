# CLI: Running sketches

PyCreative provides a small CLI wrapper to run sketches in a reproducible way. Use the CLI when you want to run sketches from the command line, in CI, or when you need to control runtime flags such as headless mode or a maximum number of frames.

Usage

- Run a sketch directly (runs the sketch's `Sketch` subclass or `main`/`run` entrypoint):

```sh
pycreative examples/curve_example.py
```

- Run headless (useful in CI or when no display is available):

```sh
pycreative examples/curve_example.py --headless
```

- Run for a limited number of frames and then exit (useful for automated testing or rendering a single frame):

```sh
pycreative examples/curve_example.py --max-frames 5
```

How headless works

- The CLI sets the environment variable `SDL_VIDEODRIVER=dummy` when `--headless` is passed. This must be set before importing `pygame` so that the SDL backend is selected early.
- If you run a sketch module directly (e.g., `python examples/curve_example.py`) and it imports `pygame` at module import time, the sketch itself must handle setting `SDL_VIDEODRIVER` early. To avoid editing example sketches, see the `examples/run_example.py` helper below.

Examples helper

For convenience, `examples/run_example.py` is a small wrapper that sets headless and forwards `--max-frames` to the CLI runner. This allows you to run any example without changing the example source:

```sh
python examples/run_example.py examples/curve_example.py --headless --max-frames 1
```

Notes

- Prefer running sketches via the `pycreative` CLI (installed entry point) or `examples/run_example.py` during development/CI to ensure consistent behavior across platforms.
- If you install the package (`pip install -e .`) the `pycreative` command will be available and the CLI will ensure `SDL_VIDEODRIVER` is set early when `--headless` is used.

Troubleshooting

- If the display still appears despite `--headless`, check whether the sketch module sets or imports `pygame` before the CLI process had a chance to set `SDL_VIDEODRIVER`. Use `examples/run_example.py` or update the sketch to delay importing `pygame` until runtime (inside `setup()` or under `if __name__ == '__main__'`).
