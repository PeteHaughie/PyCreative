[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# scale()

## Class

PCShape

## Description

Increases or decreases the size of a shape by expanding and contracting vertices. Shapes always scale from the relative origin of their bounding box. Scale values are specified as decimal percentages. For example, the method call `scale(2.0)` increases the dimension of a shape by 200%. Subsequent calls to the method multiply the effect. For example, calling `scale(2.0)` and then `scale(1.5)` is the same as `scale(3.0)`. This transformation is applied directly to the shape, it's not refreshed each time `draw()` is run.

## Examples

```py
def setup(self):
  self.s = self.load_shape("bot.svg")

def draw(self):
  self.background(204)
  self.shape(self.s)

def mouse_pressed(self):
  # Shrink the shape 90% each time the mouse is pressed
  self.s.scale(0.9)
```

## Syntax

sh.scale(s)	
sh.scale(x, y)	
sh.scale(x, y, z)	

## Parameters

| Input | Description |
|-------|-------------|
| sh	(PCShape) | any variable of type PCShape |
| s	(float) | percentage to scale the object |
| x	(float) | ercentage to scale the object in the x‑axis |
| y	(float) | percentage to scale the object in the y‑axis |
| z	(float) | percentage to scale the object in the z‑axis |

## Return

None

## Related

- [PCShape::rotate()](/docs/api/shape/PCShape/PCShape_rotate_.md)
- [PCShape::translate()](/docs/api/shape/PCShape/PCShape_translate_.md)
- [PCShape::reset_matrix()](/docs/api/shape/PCShape/PCShape_reset_matrix_.md)
