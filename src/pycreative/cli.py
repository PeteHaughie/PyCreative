"""Command-line runner for pycreative sketches.

Provides a tiny entrypoint `pycreative` (configured in pyproject.toml) that
loads a sketch file and runs it via the `core.engine.Engine` shim. The CLI
keeps things small so it can be used during development and in CI.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
import logging
import os


def _load_sketch_from_path(path: Path):
	"""Load a sketch module using the project's loader utility.

	This keeps sketch files free of loader plumbing — the CLI will ensure
	sibling imports inside the sketch file resolve correctly.
	"""
	try:
		# import here after repo src has been added to sys.path in main
		from core.util.loader import load_module_from_path
	except Exception as exc:
		raise SystemExit(f'Failed to import loader: {exc}')
	return load_module_from_path(str(path))


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(
		prog='pycreative',
		description='Run a pycreative sketch',
	)
	parser.add_argument(
		'sketch',
		type=str,
		help='Path to sketch .py file to run',
	)
	parser.add_argument(
		'--headless',
		action='store_true',
		help='Run in headless mode (no GPU/window)',
	)
	parser.add_argument(
		'--max-frames',
		type=int,
		default=None,
		help=('Run the sketch for N frames and exit (omit for interactive '
			  'window)'),
	)
	parser.add_argument(
		'--present-mode',
		type=str,
		default=None,
		choices=['vbo', 'blit', 'immediate'],
		help='Force presenter mode: vbo|blit|immediate',
	)
	parser.add_argument(
		'--force-gles',
		action='store_true',
		help='Force using GLES shader variant for testing',
	)
	parser.add_argument(
		'--verbose',
		action='store_true',
		help='Print recorded graphics commands each frame',
	)
	args = parser.parse_args(argv)

	sketch_path = Path(args.sketch)
	if not sketch_path.exists():
		print(f'Sketch not found: {sketch_path}')
		return 2

	# ensure package source path is available for imports like `core.engine`
	repo_src = Path(__file__).resolve().parents[1] / 'src'
	sys.path.insert(0, str(repo_src))

	# Optionally enable logging debug output when lifecycle debug is requested.
	# Many internal diagnostic messages use the logging module; enable a
	# basicConfig here when the environment requests lifecycle debug so
	# developers see presenter/replayer logs during runs.
	try:
		if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1' or os.getenv('PYCREATIVE_DEBUG_BLEND', '') == '1':
			logging.basicConfig(level=logging.DEBUG)
	except Exception:
		pass

	# load the sketch module
	sketch_mod = _load_sketch_from_path(sketch_path)

	try:
		engine_mod = importlib.import_module('core.engine')
		Engine = getattr(engine_mod, 'Engine')
	except Exception as exc:
		print(f'Failed to import core.engine: {exc}')
		return 3

	eng = Engine(
		sketch_module=sketch_mod,
		headless=args.headless,
		present_mode=args.present_mode,
		force_gles=bool(args.force_gles),
	)
	# attach verbose flag so Engine can optionally print commands
	setattr(eng, '_verbose', bool(args.verbose))
	if args.headless:
		# headless default: if user didn't supply max-frames, run a single frame
		frames = 1 if args.max_frames is None else int(args.max_frames)
		# If the CLI specified max-frames, force running that many frames and
		# ignore the sketch's no_loop() request so CI/debug runs behave
		# deterministically.
		if args.max_frames is None:
			eng.run_frames(frames)
		else:
			eng.run_frames(frames, ignore_no_loop=True)
		cmd_count = len(eng.graphics.commands)
		print(f'Ran sketch for {frames} frame(s); recorded commands: {cmd_count}')
		if getattr(eng, '_verbose', False):
			# Print recorded commands once (do not produce a replay per-command)
			for cmd in eng.graphics.commands:
				print(cmd)
			# Optionally produce a single offscreen PNG replay for debugging
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
		# windowed mode: start() will block until the frames complete.
		# Omit max_frames for an interactive session that stays open until closed.
		mf = None if args.max_frames is None else int(args.max_frames)
		eng.start(max_frames=mf)
		if getattr(eng, '_verbose', False):
			# In windowed mode, Engine.start() may have printed frames.
			# Print final command list.
			for cmd in eng.graphics.commands:
				print(cmd)
		print('Windowed run complete')
	return 0


if __name__ == '__main__':
	raise SystemExit(main())
