````markdown
# Running sketches via the package entrypoint

PyCreative supports running sketches by invoking the package as a module. This
is convenient for local development and avoids requiring a separate installed
`pycreative` console script.

Usage

```sh
python -m pycreative path/to/sketch.py [--flags ...]
```

Behavior

- The module entrypoint executes the provided `sketch.py` file using Python's
  `runpy.run_path()` as `__main__`. This means `if __name__ == '__main__'` blocks
  in the sketch will run as expected.
- Any trailing arguments after the sketch path are forwarded to the sketch via
  `sys.argv` (i.e., `sys.argv[0]` will be the sketch path and subsequent
  entries are the passed args).

Examples

Run a sketch normally:

```sh
python -m pycreative examples/my_sketch.py
```

Run headless with CLI-style flags (forwarded to the sketch or processed by the
CLI runner when present):

```sh
python -m pycreative examples/my_sketch.py --headless --max-frames 1
```

Notes

- If you later add packaging metadata (`pyproject.toml`) you can add an
  installable `pycreative` console script which will provide the same
  convenience. The module entrypoint is a zero-install alternative.
- The CLI wrapper and package entrypoint are complementary: the CLI may
  provide extra environment setup (e.g., early `SDL_VIDEODRIVER` handling for
  headless runs) while `python -m pycreative` is a simple, reproducible runner
  that forwards args to your sketch.

````
