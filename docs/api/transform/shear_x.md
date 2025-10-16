[docs](/docs/)→[api](/docs/api)→[transform](/docs/api/transform/)→[shear_x()](/docs/api/transform/shear_x_.md)

# shear_x()

## Description

Shears a shape around the x-axis the amount specified by the angle parameter. Angles should be specified in radians (values from 0 to PI*2) or converted to radians with the `radians()` function. Objects are always sheared around their relative position to the origin and positive numbers shear objects in a clockwise direction. Transformations apply to everything that happens after and subsequent calls to the function accumulates the effect. For example, calling `shear_x(self.PI/2)` and then `shear_x(self.PI/2)` is the same as `shear_x(self.PI)`. If `shear_x()` is called within the `draw()`, the transformation is reset when the loop begins again.

Technically, `shear_x()` multiplies the current transformation matrix by a rotation matrix. This function can be further controlled by the `push_matrix()` and `pop_matrix()` functions.

## Example

```py
self.size(400, 400)
self.translate(self.width/4, self.height/4)
self.shear_x(self.PI/4.0)
self.rect(0, 0, 120, 120)
```

## Syntax

shear_x(angle)

## Parameters

| Input | Description |
|-------|-------------|
| angle	(float) | the angle of shear, specified in radians |

## Return

None

## Related

- [pop_matrix()](/docs/api/transform/pop_matrix_.md)
- [push_matrix()](/docs/api/transform/push_matrix_.md)
- [shear_y()](/docs/api/transform/shear_y_.md)
- [scale()](/docs/api/transform/scale_.md)
- [translate()](/docs/api/transform/translate_.md)
- [radians()](/docs/api/math/trigonometry/radians_.md)