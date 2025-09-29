# PImage-style helpers

This page documents the `get()`, `set()`, `copy()` helpers and the `pixels()` context manager.

- `with surface.pixels() as pv:` yields a `PixelView` and writes changes back on exit.
- `surface.get(x,y)` -> (r,g,b) or (r,g,b,a)
- `surface.get(x,y,w,h)` -> `OffscreenSurface` (clipped region)
- `surface.set(x,y,color)` -> set single pixel (prints a hint if out-of-bounds)
- `surface.set(x,y,img)` -> blit image at x,y
- `surface.copy(...)` -> copy and optionally scale between regions or from another surface

These helpers are implemented using `pygame`'s blit and transform primitives so
they are reasonably fast and avoid Python-level loops for copying and scaling.

Examples (Processing-style):

```py
# copy a right-half of an image into the left half
flowers = self.load_image('flowers.jpg')
W = self.width
x = W // 2
flowers.copy(x, 0, x, self.height, 0, 0, x, self.height)

# get the entire image
img = self.get()

# get a pixel
c = self.get(25, 25)

# set a pixel
self.set(120, 80, (0,0,0))

# set an image at position
self.set(0, 0, img)
```
