"""Engine: minimal lifecycle implementation for tests and development.

This file intentionally contains a small, well-tested stub implementation used
to drive TDD (Red → Green → Refactor). The Engine is the single event-loop
authority in the framework; this minimal class provides the expected public
surface (`start`, `stop`, `register_api`) while keeping behavior easy to
extend.
"""

from typing import Any, List
import threading
from src.core.debug import debug
import time

class Engine:
	"""Minimal Engine used by tests and examples.

	Public contract:
	- start(): begin the engine loop (non-blocking in this stub)
	- stop(): stop the engine
	- register_api(api): register an API object for later use
	"""

	def __init__(self) -> None:
		self._running: bool = False
		self._apis: List[Any] = []

	def start(self, max_frames: int | None = None, headless: bool = False, background: bool = False, use_opengl: bool = False) -> None:
		"""Start the engine. Stub: sets running flag.

		Parameters:
		- max_frames: optional int to limit frame count (testable shutdown)
		- headless: when True, run without opening a display window
		"""
		self._running = True
		self._max_frames = max_frames
		self._headless = headless
		# If a graphics adapter was registered (via register_api), attempt to
		# create a skia surface using the graphics helper. This keeps the
		# Engine free of direct skia imports and allows adapter injection for tests.
		try:
			from src.core import graphics
			adapter = getattr(self, "_graphics_adapter", None)
			if adapter is not None:
				self._skia_surface = graphics.attach_skia_to_pygame(None, adapter=adapter)
		except Exception:
			# Swallow errors in this minimal stub: the real engine should log/raise as appropriate
			self._skia_surface = None

		# Renderer wiring: if a draw adapter has been registered (engine._draw_adapter)
		# create a Renderer and call it each frame using descriptors returned by
		# the sketch's draw() method. This simple loop is test-friendly and
		# non-blocking for now.
		renderer = None
		try:
			from src.core.renderer import Renderer
			draw_adapter = getattr(self, "_draw_adapter", None)
			if draw_adapter is not None:
				renderer = Renderer(draw_adapter)
		except Exception:
			renderer = None

		# If a background run was requested, spawn a thread to execute run().
		if background:
			# Start run() in background; pass max_frames (may be None for indefinite run)
			self._thread = threading.Thread(target=self.run, args=(max_frames, headless), daemon=True)
			self._thread.start()
			return

		# If running headful (not headless) and a display adapter is registered,
		# create a real display surface and attach a skia surface if possible.
		if not headless:
			display_adapter = getattr(self, '_display_adapter', None)
			graphics_adapter = getattr(self, '_graphics_adapter', None)
			debug(f"Engine.start: display_adapter={display_adapter}, graphics_adapter={graphics_adapter}, use_opengl={use_opengl}")
			if display_adapter is not None:
				try:
					# Create the display surface, optionally requesting an OpenGL
					# context so GPU-backed Skia surfaces can attach to it.
					surface = display_adapter.create_display_surface(use_opengl=use_opengl)
					self._display_surface = surface
					dbg_size = getattr(surface, 'get_size', lambda: (None, None))()
					debug(f"Display surface created: type={type(surface)} size={dbg_size}")
					# If we have a graphics adapter (skia) and it exposes a GPU
					# creation helper, ask it to create a GPU-backed surface. This
					# must happen after the display/GL context exists.
					if graphics_adapter is not None:
						create_gpu = getattr(graphics_adapter, 'create_gpu_surface', None)
						# Only attempt GPU-backed creation if the caller explicitly
						# requested an OpenGL context; creating a GPU context when no
						# GL context exists can block or fail on some platforms.
						if callable(create_gpu) and use_opengl:
							try:
								# Use the display surface size when possible
								w, h = getattr(surface, 'get_size', lambda: (None, None))()
								# Fall back to default sizes if unavailable
								if w is None or h is None:
									w, h = 640, 480
								self._skia_surface = create_gpu(w, h)
								debug(f"After create_gpu_surface: _skia_surface={self._skia_surface}")
							except Exception:
								self._skia_surface = None
						else:
							# Either no GPU helper is present or OpenGL wasn't requested;
							# attach a CPU-backed skia surface via the graphics helper.
							try:
								from src.core import graphics
								self._skia_surface = graphics.attach_skia_to_pygame(surface, adapter=graphics_adapter)
							except Exception:
								self._skia_surface = None
				except Exception:
					# ignore display creation errors
					pass

		# Otherwise run synchronously; if max_frames is None this will run until stop()
		self.run(max_frames=max_frames, headless=headless)
		return


	def run(self, max_frames: int, headless: bool = False) -> None:
		"""Run a simple synchronous frame loop for `max_frames` frames.

		This is a small, testable loop used by tests. In a full runtime this
		would integrate with the event loop or run on a dedicated thread.
		"""
		# Prepare renderer if a draw adapter is present
		try:
			from src.core.renderer import Renderer
			draw_adapter = getattr(self, "_draw_adapter", None)
			if draw_adapter is not None:
				renderer = Renderer(draw_adapter)
			else:
				renderer = None
		except Exception:
			renderer = None

		frames = 0
		try:
			while (max_frames is None and self._running) or (max_frames is not None and frames < max_frames):
				# Loop iteration debug
				debug(f"Engine.run loop iteration frames={frames} running={self._running}")

				# Pump events (best-effort)
				try:
					import pygame as _pg  # type: ignore
					try:
						events = _pg.event.get()
					except Exception:
						try:
							_pg.event.pump()
							events = []
						except Exception:
							events = []
					for ev in events:
						if getattr(ev, 'type', None) == _pg.QUIT:
							self.stop()
							break
						if getattr(ev, 'type', None) == _pg.KEYDOWN and getattr(ev, 'key', None) == _pg.K_ESCAPE:
							self.stop()
				except Exception:
					# pygame not available or event pump failed
					pass

				# Call sketch draw if attached
				sketch = getattr(self, "_sketch", None)
				if sketch is not None and hasattr(sketch, 'draw'):
					try:
						descriptors = sketch.draw()
						if descriptors and renderer is not None:
							renderer.render(descriptors)
						# After rendering a frame, present if we have adapters available
						graphics_adapter = getattr(self, '_graphics_adapter', None)
						display_adapter = getattr(self, '_display_adapter', None)
						if graphics_adapter is not None and display_adapter is not None and getattr(self, '_skia_surface', None) is not None:
							try:
								graphics_adapter.present(self._skia_surface, getattr(self, '_display_surface', None))
							except Exception:
								# ignore present errors
								pass
					except Exception:
						# Ignore sketch draw errors in this minimal stub
						pass

				frames += 1
				# Avoid a tight busy loop; sleep briefly
				time.sleep(0.01)
		except Exception:
			# Ensure we clear running on unexpected errors too
			pass
		finally:
			self._running = False
			thr = getattr(self, '_thread', None)
			if thr is not None and not thr.is_alive():
				try:
					delattr(self, '_thread')
				except Exception:
					pass


	def stop(self) -> None:
		"""Stop the engine. Stub: clears running flag."""
		self._running = False
		# If a background thread exists, join it to ensure a clean stop.
		thr = getattr(self, '_thread', None)
		if thr is not None and thr.is_alive():
			thr.join(timeout=1.0)

	def register_api(self, api: Any) -> None:
		"""Register an API object (stored for later wiring)."""
		self._apis.append(api)
		# If the API exposes a register_api(engine) hook, call it now so the
		# API can perform wiring with the Engine.
		if hasattr(api, "register_api"):
			try:
				api.register_api(self)
			except Exception:
				# Do not let API wiring errors break engine registration; callers
				# may want to handle errors explicitly. Keep this predictable for tests.
				pass

	@property
	def running(self) -> bool:
		"""Return whether the engine is currently running."""
		return self._running

	@property
	def apis(self) -> List[Any]:
		"""Return registered API objects."""
		return list(self._apis)

# src/core/engine.py