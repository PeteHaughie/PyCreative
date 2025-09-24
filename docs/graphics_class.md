# Graphics API (pycreative.graphics)

## Overview
The `pycreative.graphics` module provides the `Surface` class, a wrapper around `pygame.Surface` with ergonomic drawing primitives for creative coding. All drawing methods are chainable and designed for clarity and rapid prototyping.

### Stroke and Fill: Processing, openFrameworks, and PyCreative

**Processing:**
- Uses global state for fill and stroke.
- `fill(r, g, b)` sets the fill color for all subsequent shapes.
- `stroke(r, g, b)` sets the stroke color; `strokeWeight(w)` sets the stroke width.
- `noFill()` and `noStroke()` disable fill or stroke globally.
- Each shape uses the current global style unless changed.

**openFrameworks:**
- Uses global state for color and fill mode.
- `ofSetColor(r, g, b)` sets the color for both fill and stroke.
- `ofFill()` and `ofNoFill()` toggle between filled and outlined shapes.
- Stroke width is set with `ofSetLineWidth(w)`.
- No separate stroke color; fill and stroke share the same color.

**PyCreative:**
- Supports both global style and per-call overrides for fill, stroke, and stroke width.
- You can set global style with `fill()`, `stroke()`, `stroke_weight()`, `noFill()`, `noStroke()`.
- Each primitive (`rect`, `ellipse`, `triangle`, `quad`, `arc`, `bezier`) accepts per-call `fill`, `stroke`, and `stroke_width` arguments to override global state.
- This allows both Processing-like global workflows and explicit per-shape styling for maximum flexibility.

**Summary:**
- Processing and openFrameworks use global state, but differ in how fill/stroke are handled.
- PyCreative lets you choose: use global state for convenience, or override per shape for clarity and control.


## Surface Class

```python
def __init__(self, surface: pygame.Surface):
    self.surface = surface
```
### Drawing Primitives
- All methods return `self` for chainability.

#### Rectangle
```python
surf.rect(x, y, w, h, color=(255,255,255), width=0)
```
Draw a rectangle at `(x, y)` with width `w` and height `h`.
- `color`: RGB tuple
```
surf.ellipse(x, y, w, h, color=(255,255,255), width=0)
```
Draw an ellipse centered at `(x, y)`.

#### Line

```python
surf.line(x1, y1, x2, y2, color=(255,255,255), width=1)
```

Draw a line from `(x1, y1)` to `(x2, y2)`.

```
surf.triangle(x1, y1, x2, y2, x3, y3, color=(255,255,255), width=0)
```
Draw a triangle with three vertices.


#### Quad
```python
surf.quad(x1, y1, x2, y2, x3, y3, x4, y4, color=(255,255,255), width=0)
```
Draw a quadrilateral with four vertices.

#### Arc
```python
surf.arc(x, y, w, h, start_angle, end_angle, color=(255,255,255), width=1, mode="open", segments=100)
```
Draw an arc centered at `(x, y)` from `start_angle` to `end_angle` (radians).
- `mode`: 'open', 'chord', or 'pie'
- `segments`: Number of segments for curve approximation

#### Bezier Curve
```python
surf.bezier(x1, y1, x2, y2, x3, y3, x4, y4, color=(255,255,255), width=1, segments=100)
```
Draw a cubic Bezier curve from `(x1, y1)` to `(x4, y4)` with control points `(x2, y2)`, `(x3, y3)`.

#### Image
```python
surf.image(img, x, y, w=None, h=None)
```
Draw a `pygame.Surface` image at `(x, y)`. If `w` and `h` are provided, scale the image.

## Usage Example
```python
import pygame
from pycreative.graphics import Surface

screen = pygame.display.set_mode((640, 480))
surf = Surface(screen)
surf.rect(10, 10, 100, 50, color=(255,0,0))\
    .ellipse(320, 240, 200, 100, color=(0,255,0))\
    .line(0, 0, 640, 480, color=(0,0,255), width=3)
```

## Notes
- All coordinates and sizes are in pixels.
- Colors are RGB tuples.
- All drawing methods are chainable for concise code.
- For more advanced graphics, subclass `Surface` or use PyGame/OpenGL directly.

---
For full API details, see `src/pycreative/graphics.py`.
