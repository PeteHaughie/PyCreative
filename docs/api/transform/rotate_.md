[docs](/docs/)→[api](/docs/api)→[transform](/docs/api/transform/)→[rotate()](/docs/api/transform/rotate_.md)

# rotate()

## Description

Rotates a shape the amount specified by the angle parameter. Angles should be specified in radians (values from 0 to TWO_PI) or converted to radians with the `radians()` function.

Objects are always rotated around their relative position to the origin and positive numbers rotate objects in a clockwise direction. Transformations apply to everything that happens after and subsequent calls to the function accumulates the effect. For example, calling `rotate(self.HALF_PI)` and then `rotate(self.HALF_PI)` is the same as `rotate(self.PI)`. All transformations are reset when `draw()` begins again.

Technically, `rotate()` multiplies the current transformation matrix by a rotation matrix. This function can be further controlled by the `pushMatrix()` and `popMatrix()`.

## Example

```py
self.size(400, 400)
self.translate(self.width / 2, self.height / 2)
self.rotate(self.PI/3.0)
self.rect(-104, -104, 208, 208)
```

## Syntax

rotate(angle)

## Parameters

| Input | Description |
|-------|-------------|
| angle	(float) | the angle of rotation, specified in radians |

## Return

None

## Related

- [pop_matrix()](/docs/api/transform/pop_matrix_.md)
- [push_matrix()](/docs/api/transform/push_matrix_.md)
- [rotate_x()](/docs/api/transform/rotate_x_.md)
- [rotate_y()](/docs/api/transform/rotate_y_.md)
- [rotate_z()](/docs/api/transform/rotate_z_.md)
- [scale()](/docs/api/transform/scale_.md)
- [radians()](/docs/api/math/trigonometry/radians_.md)