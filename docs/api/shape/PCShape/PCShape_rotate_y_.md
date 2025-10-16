[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# rotate_y()

## Class

PCShape

## Description

Rotates a shape around the x-axis the amount specified by the angle parameter. Angles should be specified in radians (values from `0` to `TWO_PI`) or converted to radians with the `radians()` method.

Shapes are always rotated around the upper-left corner of their bounding box. Positive numbers rotate objects in a clockwise direction. Subsequent calls to the method accumulates the effect. For example, calling `rotate_y(self.HALF_PI)` and then `rotate_y(self.HALF_PI)` is the same as `rotate_y(self.PI)`. This transformation is applied directly to the shape, it's not refreshed each time `draw()` is run.

## Examples

```py
def setup(self):
  self.size(100, 100)
  self.s = self.load_shape("ohio.svg")

def draw(self):
  self.background(204)
  self.shape(self.s)

def mouse_pressed(self):
  # Rotate the shape around the y axis each time the mouse is pressed
  self.s.rotate_y(0.1)
```

## Syntax

sh.rotate(angle)	

## Parameters

| Input | Description|
|-------|------------|
| sh	(PCShape) | any variable of type PCShape |
| angle	(float) | angle of rotation specified in radians |

## Return

None

## Related

- [PCShape::rotate()](/docs/api/shape/PCShape/PCShape_rotate_.md)
- [PCShape::rotateX()](/docs/api/shape/PCShape/PCShape_rotate_x_.md)
- [PCShape::rotateZ()](/docs/api/shape/PCShape/PCShape_rotate_z_.md)
- [PCShape::scale()](/docs/api/shape/PCShape/PCShape_scale_.md)
- [PCShape::translate()](/docs/api/shape/PCShape/PCShape_translate_.md)
- [PCShape::reset_matrix()](/docs/api/shape/PCShape/PCShape_reset_matrix_.md)