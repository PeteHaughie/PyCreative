"""Command-line entry point for pycreative.

This minimal CLI is intentionally small and test-friendly. It parses a
sketch path and optional flags `--max-frames` and `--headless`, imports the
sketch as a module, constructs an Engine, registers any APIs provided by the
sketch (via a `register_api` hook), calls sketch.setup(), and starts the
engine with the parsed flags.

The implementation follows a TDD-friendly pattern: keep heavy imports out of
the CLI and allow tests to monkeypatch the Engine class via
`pycreative.core.engine.Engine`.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from typing import Optional


def parse_args(argv: Optional[list[str]] = None):
	parser = argparse.ArgumentParser(prog='pycreative')
	parser.add_argument('sketch', help='Path to the sketch module (python file)')
	parser.add_argument('--max-frames', '-m', type=int, default=None,
						help='Stop after N frames (for testing/headless runs)')
	parser.add_argument('--headless', action='store_true', help='Run without opening a window')
	return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
	args = parse_args(argv or None)

	# Import Engine via the package import path so tests can monkeypatch it
	try:
		from pycreative.core.engine import Engine
	except Exception:
		# Fallback to local import path used in development
		from src.core.engine import Engine  # type: ignore

	# Import the sketch module by filename
	sketch_module_name = args.sketch
	if sketch_module_name.endswith('.py'):
		sketch_module_name = sketch_module_name[:-3]

	sketch_mod = importlib.import_module(sketch_module_name)

	# Sketch API contract: the module exposes a Sketch class
	Sketch = getattr(sketch_mod, 'Sketch', None)
	if Sketch is None:
		print('Sketch module must define a Sketch class', file=sys.stderr)
		return 2

	sketch = Sketch()
	if hasattr(sketch, 'setup'):
		try:
			sketch.setup()
		except Exception:
			# Setup failures should be visible but not crash tests here
			pass

	# Prefer using a bootstrap helper to centralize engine/adapters wiring.
	try:
		from src.core.bootstrap import build_engine
	except Exception:
		# try package path for installed layout
		from pycreative.core.bootstrap import build_engine  # type: ignore

	engine = build_engine()

	# Allow the sketch module to register APIs via a module-level hook
	if hasattr(sketch_mod, 'register_api'):
		try:
			sketch_mod.register_api(engine)
		except Exception:
			pass

	# Start engine with flags
	engine.start(max_frames=args.max_frames, headless=args.headless)
	return 0


if __name__ == '__main__':
	raise SystemExit(main())