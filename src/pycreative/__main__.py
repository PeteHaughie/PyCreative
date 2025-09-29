"""Entry point for the pycreative package.

Allows running sketches like:

    python -m pycreative examples/my_sketch.py

This module will execute the provided Python file as __main__ and forward
command-line arguments to it.
"""
from __future__ import annotations

import argparse
import runpy
import sys


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv) if argv is None else list(argv)
    parser = argparse.ArgumentParser(prog="pycreative", description="Run a pycreative sketch file")
    parser.add_argument("sketch", nargs="?", help="Path to a sketch Python file to run")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed to the sketch")
    ns = parser.parse_args(argv[1:])

    if not ns.sketch:
        parser.print_help()
        return 2

    sketch_path = ns.sketch
    # Forward remaining args to the sketch as sys.argv (common expectation)
    sys.argv[:] = [sketch_path] + (ns.args or [])

    # Execute the sketch file as __main__ so if __name__ == '__main__' blocks run.
    try:
        runpy.run_path(sketch_path, run_name="__main__")
        return 0
    except FileNotFoundError:
        print(f"pycreative: file not found: {sketch_path}", file=sys.stderr)
        return 3
    except SystemExit:
        # propagate real sys.exit calls
        raise
    except Exception:
        # Print a short traceback and return non-zero so CI can detect failure
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
