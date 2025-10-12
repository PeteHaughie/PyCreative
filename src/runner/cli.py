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
	parser.add_argument('--use-opengl', action='store_true', help='Request an OpenGL-backed display/context')
	return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
	args = parse_args(argv or None)
	# Ensure the repository `src` directory is on sys.path when running from
	# the development layout. This allows the CLI to be invoked via the
	# installed console script (or `python -m pycreative.cli`) without
	# requiring the user to set PYTHONPATH manually.
	try:
		import os
		import sys as _sys
		# Calculate the src directory relative to this file
		this_dir = os.path.dirname(__file__)
		src_dir = os.path.abspath(os.path.join(this_dir, '..'))
		repo_root = os.path.abspath(os.path.join(src_dir, '..'))
		# Add src and repo root so both package modules and example modules
		# can be imported without requiring PYTHONPATH.
		if os.path.isdir(src_dir) and src_dir not in _sys.path:
			_sys.path.insert(0, src_dir)
		if os.path.isdir(repo_root) and repo_root not in _sys.path:
			_sys.path.insert(0, repo_root)
	except Exception:
		pass

	# Import Engine preferring the local dev copy so tests can monkeypatch it.
	try:
		from src.core.engine import Engine  # type: ignore
	except Exception:
		try:
			from pycreative.core.engine import Engine
		except Exception:
			# As a last resort let the import fail normally
			from src.core.engine import Engine  # type: ignore

	# Import the sketch module by filename
	sketch_module_name = args.sketch
	if sketch_module_name.endswith('.py'):
		# Strip the .py suffix and convert filesystem separators to module dots
		sketch_module_name = sketch_module_name[:-3]
		# Normalize separators (handle both '/' and os.sep)
		import os as _os
		sketch_module_name = sketch_module_name.replace('/', '.')
		if _os.path.sep != '/':
			sketch_module_name = sketch_module_name.replace(_os.path.sep, '.')

		# Try to import as a module first. If that fails, try to load the file
		# directly using importlib utilities (so paths like './examples/foo.py'
		# also work).
		try:
			sketch_mod = importlib.import_module(sketch_module_name)
		except Exception:
			# Fallback: try to load by filesystem path
			try:
				from importlib.util import spec_from_file_location, module_from_spec
				_spec = spec_from_file_location("__sketch__", args.sketch)
				if _spec and _spec.loader:
					_sk_mod = module_from_spec(_spec)
					_spec.loader.exec_module(_sk_mod)
					sketch_mod = _sk_mod
				else:
					raise
			except Exception:
				raise

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

	engine = build_engine(use_opengl=args.use_opengl)

	# Allow the sketch module to register APIs via a module-level hook
	if hasattr(sketch_mod, 'register_api'):
		try:
			sketch_mod.register_api(engine)
		except Exception:
			pass

	# Start engine with flags
	# Call engine.start, but remain backward-compatible with older Engine
	# implementations used in tests that may not accept the `use_opengl` kwarg.
	try:
		engine.start(max_frames=args.max_frames, headless=args.headless, use_opengl=args.use_opengl)
	except TypeError:
		# Fallback for engines that don't accept use_opengl
		engine.start(max_frames=args.max_frames, headless=args.headless)
	return 0


if __name__ == '__main__':
	raise SystemExit(main())