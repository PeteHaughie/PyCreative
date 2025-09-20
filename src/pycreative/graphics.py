"""
pycreative.graphics: Surface wrapper and drawing helpers for PyCreative.
"""
import pygame
from typing import Tuple, Optional, Any

class Surface:
	"""
	Wrapper for pygame.Surface with drawing helpers.

	Usage example:
	>>> surf = Surface(pygame.Surface((640, 480)))
	>>> surf.rect(10, 10, 100, 50, color=(255,0,0))
	>>> surf.ellipse(320, 240, 200, 100, color=(0,255,0))
	>>> surf.line((0,0), (640,480), color=(0,0,255), width=3)
	>>> surf.image(pygame.image.load("example.png"), 50, 50)
	"""
	def __init__(self, surface: pygame.Surface):
		self.surface = surface

	def rect(self, x: float, y: float, w: float, h: float, color: Any = (255,255,255), width: int = 0):
		pygame.draw.rect(self.surface, color, (x, y, w, h), width)
		return self

	def ellipse(self, x: float, y: float, w: float, h: float, color: Any = (255,255,255), width: int = 0):
		"""
		Draw an ellipse centered at (x, y) with width w and height h.
		Parameters:
		- x, y: Center coordinates
		- w, h: Width and height
		- color: RGB tuple
		- width: Border thickness (0 = filled)
		"""
		pygame.draw.ellipse(self.surface, color, (x-w/2, y-h/2, w, h), width)
		return self

	def line(self, start: Tuple[float, float], end: Tuple[float, float], color: Any = (255,255,255), width: int = 1):
		pygame.draw.line(self.surface, color, start, end, width)
		return self

	def image(self, img: pygame.Surface, x: float, y: float):
		self.surface.blit(img, (x, y))
		return self
