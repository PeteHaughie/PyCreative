# Pixels API

PyCreative exposes simple, copy-based pixel helpers on `Surface` and `OffscreenSurface`.

Key methods

- `get_pixels()` -> returns a H x W x C uint8 array (preferably a numpy array) where C is 3 (RGB) or 4 (RGBA).
- `set_pixels(arr)` -> write a H x W x C array back into the surface. Accepts array-like inputs.
- `get_pixel(x, y)` -> returns a (r,g,b) or (r,g,b,a) tuple for the given pixel.
- `set_pixel(x, y, color)` -> set a single pixel. `color` may be an (r,g,b) or (r,g,b,a) tuple.

Notes

- The public API normalizes arrays to shape (height, width, channels) even though some pygame surfarray helpers use (width, height, channels). This choice maps naturally to row-major array conventions (first index is y).
- Default behavior is copy-based and safe. For high-performance, in-place access may be added later via a context-manager API.
- The implementation prefers numpy + `pygame.surfarray` when available and falls back to per-pixel `get_at`/`set_at` when it's not.

Example

```py
# Read-modify-write
arr = surface.get_pixels()          # (H,W,3)
arr[10:20, 10:20] = [255, 0, 0]     # paint a red square
surface.set_pixels(arr)
```

Idiomatic usage and numpy
-------------------------

The library prefers to keep sketches free of heavy, top-level imports. To that end:

- `get_pixels()` returns a PixelView object which provides a `.shape` attribute and supports `[y,x,c]` indexing. Under the hood the PixelView wraps either a numpy ndarray (fast) or a nested Python list (fallback).
- Use `surface.is_numpy_backed()` to check whether numpy-based fast paths are available. If you need numpy-only operations (vectorized transforms, broadcasting, filters), import numpy lazily inside `setup()` or `draw()` and operate on `arr.raw()` (the underlying ndarray):

```py
def draw(self):
	pv = self.surface.get_pixels()  # PixelView
	h, w, c = pv.shape
	try:
		# lazy import so module-level imports don't force numpy dependency
		import numpy as np

		if self.surface.is_numpy_backed() and hasattr(pv.raw(), 'astype'):
			arr = pv.raw()            # numpy ndarray
			# vectorized operation
			gx = np.linspace(0, 255, w, dtype=np.uint8)[np.newaxis, :, np.newaxis]
			gy = np.linspace(0, 255, h, dtype=np.uint8)[:, np.newaxis, np.newaxis]
			arr[:, :, 0] = gx[:, :, 0]
			arr[:, :, 1] = gy[:, :, 0]
			arr[:, :, 2] = 80
			self.surface.set_pixels(pv)
			return
	except Exception:
		pass

# fallback: operate on the PixelView with pure-Python loops
for y in range(h):
	gy = int(y * 255 / max(1, h - 1))
	for x in range(w):
		gx = int(x * 255 / max(1, w - 1))
		pv[y, x, 0] = gx
		pv[y, x, 1] = gy
		pv[y, x, 2] = 80
self.surface.set_pixels(pv)
```

This keeps examples and sketches idiomatic while still allowing power users to use numpy when available.
