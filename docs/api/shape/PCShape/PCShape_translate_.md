[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# translate()

## Class

PCShape

## Description

Specifies an amount to displace the shape. The `x` parameter specifies left/right translation, the `y` parameter specifies up/down translation, and the `z` parameter specifies translations toward/away from the screen. Subsequent calls to the method accumulates the effect. For example, calling `translate(50, 0)` and then `translate(20, 0)` is the same as `translate(70, 0)`. This transformation is applied directly to the shape, it's not refreshed each time `draw()` is run.

## Examples

```py
def setup(self):
  self.s = self.load_shape("bot.svg")

def draw(self):
  self.background(204)
  self.shape(self.s)

def mouse_pressed(self):
  # Move the shape 10 pixels right each time the mouse is pressed
  self.s.translate(10, 0)
```

## Syntax

sh.translate(x, y)	

sh.translate(x, y, z)	

## Parameters

| Input | Description |
|-------|-------------|
| sh	(PCShape) | any variable of type PCShape |
| x	(float) | left/right translation |
| y	(float) | up/down translation |
| z	(float) | forward/back translation |

## Return

None	

## Related

- [PCShape::rotate()](/docs/api/shape/PCShape/PCShape_rotate_.md)
- [PCShape::scale()](/docs/api/shape/PCShape/PCShape_scale_.md)
- [PCShape::reset_matrix()](/docs/api/shape/PCShape/PCShape_reset_matrix_.md)