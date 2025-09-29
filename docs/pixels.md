# Pixels API

PyCreative exposes a small, pragmatic pixels API designed to be safe for beginners and fast for power users.

Overview

- `Surface.pixels()` — context manager that yields a `PixelView` for read-modify-write access. The context manager writes pixels back to the surface when the block exits.
- `Surface.get_pixels()` / `Surface.set_pixels()` — copy-based helpers for simple read/write patterns.
- `Surface.get_pixel(x,y)` / `Surface.set_pixel(x,y,color)` — single-pixel accessors.

PixelView semantics

- The `PixelView` has `.shape` in (H, W, C) format and supports indexing as `pv[y, x, c]` or `pv[y, x]` for color tuples.
- The public `PixelView` hides whether numpy is used internally. If numpy is available and used, `pv.raw()` returns the underlying ndarray; otherwise `pv.raw()` may return a nested list-like structure.
- The context manager guarantees that any mutations are flushed back to the surface when the `with` block exits, so sketches can remain agnostic to copy-vs-inplace semantics.

Examples

Read-modify-write with the context manager (recommended):

```py
with surface.pixels() as pv:
	h, w, c = pv.shape
	for y in range(10, 20):
		for x in range(10, 20):
			pv[y, x] = (255, 0, 0, 255)
```

Copy-based usage:

```py
arr = surface.get_pixels()      # returns an array-like (H,W,C)
arr[10:20, 10:20] = [255, 0, 0]
surface.set_pixels(arr)
```

Numpy interop and vectorized ops

If your sketch needs numpy for vectorized work, import numpy lazily inside `setup()` or `draw()` and operate on `pv.raw()` when available:

```py
with surface.pixels() as pv:
	if surface.is_numpy_backed():
		arr = pv.raw()  # numpy ndarray: shape (H,W,C)
		import numpy as np
		gx = np.linspace(0, 255, arr.shape[1], dtype=np.uint8)[np.newaxis, :, np.newaxis]
		arr[:, :, 0] = gx[:, :, 0]
		# mutations are written back on context exit
	else:
		# fallback: pure Python loops
		h, w, _ = pv.shape
		for y in range(h):
			for x in range(w):
				pv[y, x, 0] = int(x * 255 / max(1, w - 1))

```

Tips
- Prefer `with surface.pixels()` for most use-cases: it keeps code simple and ensures state is synchronized.
- Use `surface.is_numpy_backed()` to detect fast-path availability if you plan to use numpy-specific constructs.
- The API keeps row-major indexing `(y,x,channel)` for compatibility with image-processing libraries and to match common Python conventions.

See also: `docs/pixels_image.md` for image-specific helpers and interoperability notes.
