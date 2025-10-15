"""Command-line runner for pycreative sketches.

Provides a tiny entrypoint `pycreative` (configured in pyproject.toml) that
loads a sketch file and runs it via the `core.engine.Engine` shim. The CLI
keeps things small so it can be used during development and in CI.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


def _load_sketch_from_path(path: Path):
	"""Dynamically load a python module from a path and return the module object.

	The sketch is expected to provide a top-level `draw(this)` function.
	"""
	spec = importlib.util.spec_from_file_location(path.stem, str(path))
	if spec is None or spec.loader is None:
		raise SystemExit(f"Can't load sketch from {path}")
	mod = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	return mod


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(prog='pycreative', description='Run a pycreative sketch')
	parser.add_argument('sketch', type=str, help='Path to sketch .py file to run')
	parser.add_argument('--headless', action='store_true', help='Run in headless mode (no GPU/window)')
	parser.add_argument('--max-frames', type=int, default=None, help='Run the sketch for N frames and exit (omit for interactive window)')
	parser.add_argument('--verbose', action='store_true', help='Print recorded graphics commands each frame')
	args = parser.parse_args(argv)

	sketch_path = Path(args.sketch)
	if not sketch_path.exists():
		print(f"Sketch not found: {sketch_path}")
		return 2

	# ensure package source path is available for imports like `core.engine`
	repo_src = Path(__file__).resolve().parents[1] / 'src'
	sys.path.insert(0, str(repo_src))

	# load the sketch module
	sketch_mod = _load_sketch_from_path(sketch_path)

	try:
		engine_mod = importlib.import_module('core.engine')
		Engine = getattr(engine_mod, 'Engine')
	except Exception as exc:
		print(f"Failed to import core.engine: {exc}")
		return 3

	eng = Engine(sketch_module=sketch_mod, headless=args.headless)
	# attach verbose flag so Engine can optionally print commands
	setattr(eng, '_verbose', bool(args.verbose))
	if args.headless:
		# headless default: if user didn't supply max-frames, run a single frame
		frames = 1 if args.max_frames is None else int(args.max_frames)
		eng.run_frames(frames)
		print(f'Ran sketch for {frames} frame(s); recorded commands: {len(eng.graphics.commands)}')
		if getattr(eng, '_verbose', False):
			for cmd in eng.graphics.commands:
				print(cmd)
				# produce an offscreen PNG replay for easier debugging (optional)
				# Prefer a Skia-backed snapshot if available (authoritative);
				# otherwise fall back to the Pillow rasteriser.
				repr_path = 'render_debug.png'
				backend_written = False
				try:
					from core.io.skia_replayer import replay_to_image_skia as _rsi
					try:
						_rsi(eng, repr_path)
						print(f'Wrote Skia offscreen replay to {repr_path}')
						backend_written = True
					except Exception as _err:
						print(f'Skia replayer failed: {_err}')
				except Exception:
					# skia-python not available or import failed; try Pillow replayer
					try:
						from core.io.replayer import replay_to_image as _rti
						try:
							_rti(eng, repr_path)
							print(f'Wrote Pillow offscreen replay to {repr_path}')
							backend_written = True
						except Exception as _err:
							print(f'Pillow replayer failed: {_err}')
					except Exception:
						print('Offscreen replayer not available (Pillow missing?)')
				if not backend_written:
					print('No offscreen snapshot could be written')
	else:
		# windowed mode: start() will block until the frames complete; omit
		# max_frames for an interactive session that stays open until closed.
		mf = None if args.max_frames is None else int(args.max_frames)
		eng.start(max_frames=mf)
		if getattr(eng, '_verbose', False):
			# In windowed mode, Engine.start() may have printed frames; print final command list
			for cmd in eng.graphics.commands:
				print(cmd)
		print('Windowed run complete')
	return 0


if __name__ == '__main__':
	raise SystemExit(main())
