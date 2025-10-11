[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# Class

PCShape

## Description

The `set_stroke()` method defines the outline color of a PCShape. This method is used after shapes are created or when a shape is defined explicitly (e.g. `create_shape(RECT, 20, 20, 80, 80)`) as shown in the below example. When a shape is created with `begin_shape()` and `end_shape()`, its attributes may be changed with `fill()` and `stroke()` within `begin_shape()` and `end_shape()`. However, after the shape is created, only the `set_stroke()` method can define a new stroke value for the PCShape.

## Examples

```py
def setup(self):  
  self.size(640, 360)
  self.circle = self.create_shape("ELLIPSE", 0, 0, 200, 200)
  self.circle.set_stroke(self.color(255))  

def draw():
  self.background(51)
  self.circle.setFill(self.color(self.random(255)))
  self.translate(self.mouse_x, self.mouse_y)
  self.shape(self.circle)
```

## Syntax

sh.setStroke(stroke)	

# Parameters

| Input | Description |
|-------|-------------|
| sh	(PCShape) | any variable of type PCShape |

## Return

pass