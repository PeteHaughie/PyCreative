# Shape Construction (begin_shape / vertex / end_shape)

This page documents PyCreative's immediate-mode shape construction helpers which mirror the familiar Processing API.

Core helpers

- `begin_shape()` — start collecting vertices for a shape.
- `vertex(x, y)` — add a vertex to the current shape.
- `end_shape(close=False)` — finish the shape and draw it. If `close=True` the shape is closed.

These helpers are implemented on `pycreative.graphics.Surface` and are available on `OffscreenSurface` instances created via `Sketch.create_graphics()`.

When to use

- Use the shape helpers when you want to construct arbitrary polygons from a sequence of points.
- For more advanced curves (beziers, curves) see the planned roadmap; the current API focuses on straight-edge polygons.

Behavior and examples

- The shape uses the current `fill()`, `stroke()`, and `stroke_weight()` state from the drawing surface. If you need to preserve or change state for the shape, call the relevant state methods before calling `begin_shape()`.
- The shape will be filled using the current fill color if a fill is set. If you only want an outline, call `fill(None)` before `begin_shape()`.
- Per-call style overrides are supported by the drawing primitives. You can pass `fill=`, `stroke=`, and `stroke_weight=` directly to `end_shape()` or to primitives that draw pre-composed shapes.

Example — draw a triangle on the main canvas

```py
from pycreative import Sketch

class TriangleSketch(Sketch):
    def setup(self):
        self.size(400, 300)

    def draw(self):
        self.clear((255, 255, 255))
        self.fill((200, 50, 50))
        self.stroke((0, 0, 0))
        self.stroke_weight(2)

        self.begin_shape()
        self.vertex(100, 50)
        self.vertex(50, 200)
        self.vertex(250, 180)
        self.end_shape(close=True)

if __name__ == '__main__':
    TriangleSketch().run()
```

Example — pre-rendered polygon in an offscreen buffer

```py
class PreRenderShape(Sketch):
    def setup(self):
        self.size(800, 600)
        self.no_loop()
        self.off = self.create_graphics(300, 200, inherit_state=True)
        with self.off:
            self.clear((0, 0, 0))
            self.fill((100, 200, 180))
            self.stroke((10, 10, 10))
            self.begin_shape()
            self.vertex(20, 20)
            self.vertex(280, 40)
            self.vertex(180, 170)
            self.vertex(40, 160)
            self.end_shape(close=True)

    def draw(self):
        self.clear((240, 240, 240))
        self.image(self.off, 50, 50)
```

Notes and tips

- `begin_shape()` resets an internal vertex buffer. Calling `begin_shape()` while another shape is active will discard the previous vertices.
- `end_shape(close=True)` connects the last vertex to the first before filling/stroking.
- For high-frequency or complex shapes, consider drawing into an `OffscreenSurface` and reusing it.

Compatibility

- These helpers are intentionally small and predictable. They match the Processing semantics for basic polygon construction. More advanced vertex types (bezierVertex, curveVertex) are on the roadmap.

If you'd like additional examples (complex star shapes, winding rules, or an SVG export example), tell me which and I'll add them to this page.
