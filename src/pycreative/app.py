"""
pycreative.app: Main Sketch class and app loop for PyCreative.
"""
import pygame
import time
from typing import Optional, Any
from pycreative.graphics import Surface

class Sketch:
	"""
	Base class for PyCreative sketches. Implements lifecycle hooks and main loop.

	Usage example:
	>>> class MySketch(Sketch):
	...     def setup(self):
	...         self.size(800, 600)
	...     def draw(self):
	...         self.clear(0)
	...         self.ellipse(self.width//2, self.height//2, 200, 200)
	...
	>>> MySketch().run()
	"""
	def __init__(self):
		self.width = 640
		self.height = 480
		self.fullscreen = False
		self.bg = 0
		self._screen: Optional[pygame.Surface] = None
		self._surface: Optional[Surface] = None
		self._clock: Optional[pygame.time.Clock] = None
		self._running = False
		self._frame_rate = 60
		self.t = 0.0
		self.frame_count = 0

	def size(self, width: int, height: int, fullscreen: bool = False):
		self.width = width
		self.height = height
		self.fullscreen = fullscreen

	def frame_rate(self, fps: int):
		self._frame_rate = fps

	def clear(self, color: Any = 0):
		if self._surface:
			self._surface.surface.fill(color)

	def ellipse(self, x: float, y: float, w: float, h: float, color: Any = (255,255,255)):
		if self._surface:
			self._surface.ellipse(x, y, w, h, color)

	def rect(self, x: float, y: float, w: float, h: float, color: Any = (255,255,255), width: int = 0):
		if self._surface:
			self._surface.rect(x, y, w, h, color, width)

	def run(self, max_frames: Optional[int] = None):
		pygame.init()
		self._running = True
		self.setup()
		flags = pygame.FULLSCREEN if self.fullscreen else 0
		self._screen = pygame.display.set_mode((self.width, self.height), flags)
		self._surface = Surface(self._screen)
		self._clock = pygame.time.Clock()
		start_time = time.time()
		while self._running:
			if max_frames is not None and self.frame_count >= max_frames:
				print(f"[Sketch.run] Reached max_frames: {self.frame_count}, closing sketch.")
				self._running = False
			dt = self._clock.tick(self._frame_rate) / 1000.0
			self.t = time.time() - start_time
			self.update(dt)
			events = list(pygame.event.get())
			if not events:
				pygame.event.pump()
			for event in events:
				self.on_event(event)
				if event.type == pygame.QUIT:
					self._running = False
			self.draw()
			pygame.display.flip()
			self.frame_count += 1
		self.shutdown()

	def setup(self):
		"""
		Override this method to add setup code for your sketch.
		"""
		pass

	def update(self, dt: float):
		"""
		Override this method to add update logic for your sketch.

		Parameters:
		- dt: Time in seconds since the last frame.
		"""
		pass

	def draw(self):
		"""
		Override this method to add drawing code for your sketch.
		"""
		pass

	def on_event(self, event: pygame.event.Event):
		"""
		Override this method to handle events in your sketch.

		Parameters:
		- event: The pygame event to handle.
		"""
		pass

	def shutdown(self):
		"""
		Override this method to add cleanup code for your sketch.
		"""
		pass
