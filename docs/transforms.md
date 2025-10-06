# Transform stack and affine helpers

PyCreative exposes a small, explicit 2D transform stack on every `Surface` so
sketch authors can perform local coordinate transforms without mutating global
state. The API is intentionally small and mirrors Processing/openFrameworks
semantics while remaining pure-Python and dependency-free.

Key APIs (on `Surface` / `OffscreenSurface`)

- `push()` / `pop()` — push a copy of the current matrix and pop it later.
- `translate(dx, dy)` — apply a translation (in pixels) to the current matrix.
- `rotate(theta)` — apply a rotation in radians.
- `scale(sx, sy=None)` — apply a scale; `sy` defaults to `sx` when omitted.
- `reset_matrix()` — reset the top matrix to the identity matrix.
- `get_matrix()` / `set_matrix(M)` — get a copy of the current 3x3 matrix or
  overwrite the top matrix with `M` (copied).
- `transform(translate=(dx,dy), rotate=theta, scale=(sx,sy))` — context
  manager that pushes, applies optional ops, yields the surface, then pops on
  exit. Example:

```py
with surface.transform(translate=(10,20), rotate=0.5):
    surface.rect(0,0,100,50)
```

Compatibility aliases

- `push_matrix()` / `pop_matrix()` — Processing-style aliases for `push()` / `pop()` are available on `Surface` and `Sketch` (they behave identically to `push()`/`pop()`).
- `CENTER` / `CORNER` — `Sketch` exposes `CENTER` and `CORNER` constants mapped to the corresponding `Surface` mode constants so examples can use `self.CENTER` when calling `rect_mode()` / `ellipse_mode()`.

Semantics and implementation notes

- Matrices are represented as 3x3 nested lists (homogeneous coordinates). The
  stack preserves the base identity matrix so `pop()` cannot remove it.
- Transform composition order: operations are applied by multiplying the
  existing (top) matrix by the operation matrix (i.e., "apply then compose"
  semantics). This matches common 2D API expectations: `translate()` then
  `rotate()` means points are first translated then rotated.
- Fast-path: many drawing primitives check whether the current matrix is the
  identity and use optimized integer drawing (pygame.draw.*). When a
  non-identity transform is active the points are transformed and primitives
  are drawn as polygons/approximations (for example transformed ellipses are
  tessellated into polygons).
- Image drawing: `Surface.image()` provides a best-effort transform path: for
  translation + uniform scale + rotation it attempts an efficient
  `pygame.transform.rotozoom()` path (angle extracted from the matrix and
  average scale applied). Non-uniform scales or shears fall back to a
  conservative blit at the transformed origin.

Performance & edge cases

- Identity fast-path avoids unnecessary math when no transforms are used —
  prefer to rely on this for simple UI elements.
- Ellipses under non-uniform transforms are approximated by polygons; this
  usually looks fine for most creative work but is not pixel-perfect.
- Stroke scaling under transforms is not automatic in the MVP: stroke widths
  are applied in device/pixel space unless you explicitly decompose the
  scale and compute adjusted stroke weights.

Examples

Rotate a local group of shapes:

```py
with surface.transform(translate=(200,150), rotate=frame_time * 0.5):
    surface.fill((255,100,100))
    surface.rect(-40, -20, 80, 40)
    surface.ellipse(0, 60, 30, 30)
```

is equivalent to:

```py
self.push()
self.translate(200, 150)
self.rotate(frame_time * 0.5)
self.fill((255, 100, 100))
self.rect(-40, -20, 80, 40)
self.ellipse(0, 60, 30, 30)
self.pop()
```

to be extra safe you can also protect the trnsformation with a try catch condition:

```py
self.push()
try:
    self.translate(...)
    ...
finally:
    self.pop()
```

Copying transforms to offscreen surfaces

If you create an offscreen surface with `Sketch.create_graphics(...,
inherit_transform=True)` the offscreen buffer's top matrix will be initialized
to a copy of the current main-surface matrix at creation time. This is useful
when you want pre-rendered content to share the same coordinate basis as the
main canvas. For dynamic linkage (copying the main matrix every frame) call
`off.set_matrix(self.surface.get_matrix())` inside `draw()` before rendering
into `off`.
