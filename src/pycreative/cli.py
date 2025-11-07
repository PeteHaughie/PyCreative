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

	# If the repository contains a project-local virtualenv at `.venv`,
	# prefer to run using that Python interpreter. This helps avoid using a
	# globally-installed `pycreative` entrypoint that points to a different
	# Python (e.g., Anaconda) and can lead to surprising backend differences
	# (skia available vs not). We do not force a re-exec by default; instead
	# we print a helpful hint. Set PYCREATIVE_AUTO_REEXEC=1 to automatically
	# re-exec into the local venv Python when present.
	try:
		import sys as _sys
		repo_root = Path(__file__).resolve().parents[2]
		venv_python = repo_root / '.venv' / 'bin' / 'python'
		if venv_python.exists():
			try:
				cur = Path(_sys.executable).resolve()
				vpy = venv_python.resolve()
				if cur != vpy:
					print(f"Detected project .venv at {venv_python}; current python is {_sys.executable}")
					print("To run with the project venv, either activate it or run:\n  .venv/bin/python -m pycreative <sketch> [args]")
					if os.getenv('PYCREATIVE_AUTO_REEXEC', '') == '1':
						# Re-exec into the venv python so the rest of the CLI runs
						# in the intended environment. Preserve argv.
						try:
							os.execv(str(vpy), [str(vpy), '-m', 'pycreative'] + list(_sys.argv[1:]))
						except Exception:
							# fall through to continue with existing interpreter
							pass
			except Exception:
				pass
	except Exception:
		pass

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
			def _sanitize_cmd(c):
				try:
					import json as _json
				except Exception:
					_json = None
				out = {'op': c.get('op'), 'args': {}, 'meta': c.get('meta')}
				args_dict = c.get('args', {}) or {}
				for k, v in args_dict.items():
					# redact image-like payloads or raw bytes
					if k in ('image', 'image_bytes'):
						out['args'][k] = '<redacted-image>'
					elif isinstance(v, (bytes, bytearray, memoryview)):
						out['args'][k] = '<redacted-bytes>'
					else:
						# keep small primitives, otherwise fall back to repr()
						try:
							if _json is not None:
								_json.dumps({k: v})
								out['args'][k] = v
							else:
								out['args'][k] = v
						except Exception:
							try:
								out['args'][k] = repr(v)
							except Exception:
								out['args'][k] = f'<{type(v).__name__}>'
				return out
			for cmd in eng.graphics.commands:
				print(_sanitize_cmd(cmd))
			# Optionally produce a single offscreen PNG replay for debugging
			repr_path = 'render_debug.png'
			# Skia-first policy: prefer the Skia replayer and fail fast if it's
			# not available. We intentionally do not fall back to Pillow here to
			# keep the runtime GPU-forward and to surface missing backend
			# configuration early for developers.
			try:
				from core.io.skia_replayer import replay_to_image_skia as _rsi
			except Exception as _imp_err:
				print('Skia replayer not available or failed to import:', _imp_err)
				print('This project is Skia-GPU-forward; please install skia-python in the active environment and retry.')
				return 4

			try:
				_rsi(eng, repr_path)
				print(f'Wrote Skia offscreen replay to {repr_path}')
			except Exception as _err:
				print(f'Skia replayer failed while rendering: {_err}')
				return 5
	else:
		# windowed mode: start() will block until the frames complete.
		# Omit max_frames for an interactive session that stays open until closed.
		mf = None if args.max_frames is None else int(args.max_frames)
		eng.start(max_frames=mf)
		if getattr(eng, '_verbose', False):
			# In windowed mode, Engine.start() may have printed frames.
			# Print final command list (sanitized to avoid dumping raw bytes).
			def _sanitize_cmd(c):
				try:
					import json as _json
				except Exception:
					_json = None
				out = {'op': c.get('op'), 'args': {}, 'meta': c.get('meta')}
				args_dict = c.get('args', {}) or {}
				for k, v in args_dict.items():
					if k in ('image', 'image_bytes'):
						out['args'][k] = '<redacted-image>'
					elif isinstance(v, (bytes, bytearray, memoryview)):
						out['args'][k] = '<redacted-bytes>'
					else:
						try:
							if _json is not None:
								_json.dumps({k: v})
								out['args'][k] = v
							else:
								out['args'][k] = v
						except Exception:
							try:
								out['args'][k] = repr(v)
							except Exception:
								out['args'][k] = f'<{type(v).__name__}>'
				return out
			for cmd in eng.graphics.commands:
				print(_sanitize_cmd(cmd))
		print('Windowed run complete')
	return 0


if __name__ == '__main__':
	raise SystemExit(main())
