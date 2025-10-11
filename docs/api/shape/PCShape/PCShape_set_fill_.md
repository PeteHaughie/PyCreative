[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# set_fill()

## Class

PCShape

## Description

The `set_fill()` method defines the fill color of a PCShape. This method is used after shapes are created or when a shape is defined explicitly (e.g. `create_shape(RECT, 20, 20, 80, 80)`) as shown in the below example. When a shape is created with `begin_shape()` and `end_shape()`, its attributes may be changed with `fill()` and `stroke()` within `begin_shape()` and `end_shape()`. However, after the shape is created, only the `set_fill()` method can define a new fill value for the PCShape.

### Examples

```py
def setup(self):
  self.size(640, 360)
  self.circle = self.create_shape("ELLIPSE", 0, 0, 200, 200)
  self.circle.set_stroke(self.color(255))

def draw(self):
  self.background(51)
  self.circle.set_fill(self.color(self.random(255)))
  self.translate(self.mouse_x, self.mouse_y)
  self.shape(self.circle)
```

## Syntax

sh.set_fill(fill)	

## Parameters

sh	(PShape)	any variable of type PShape

## Return

pass