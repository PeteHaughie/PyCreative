"""Engine: minimal lifecycle implementation for tests and development.

This file intentionally contains a small, well-tested stub implementation used
to drive TDD (Red → Green → Refactor). The Engine is the single event-loop
authority in the framework; this minimal class provides the expected public
surface (`start`, `stop`, `register_api`) while keeping behavior easy to
extend.
"""

from typing import Any, List

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

	def start(self, max_frames: int | None = None, headless: bool = False) -> None:
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

		# Delegate to run() when a frame limit is specified; otherwise return
		# immediately so start() is non-blocking by default.
		if max_frames is not None:
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
		while frames < max_frames:
			# Call sketch draw if attached
			sketch = getattr(self, "_sketch", None)
			if sketch is not None and hasattr(sketch, 'draw'):
				try:
					descriptors = sketch.draw()
					if descriptors and renderer is not None:
						renderer.render(descriptors)
				except Exception:
					# Ignore sketch draw errors in this minimal stub
					pass

			frames += 1

	def stop(self) -> None:
		"""Stop the engine. Stub: clears running flag."""
		self._running = False

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