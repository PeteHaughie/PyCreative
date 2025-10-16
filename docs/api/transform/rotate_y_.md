[docs](/docs/)→[api](/docs/api)→[transform](/docs/api/transform/)→[rotate_y()](/docs/api/transform/rotate_y_.md)

# rotate_y()

## Description

Rotates a shape around the y-axis the amount specified by the angle parameter. Angles should be specified in radians (values from 0 to PI*2) or converted to radians with the `radians()` function. Objects are always rotated around their relative position to the origin and positive numbers rotate objects in a counterclockwise direction. Transformations apply to everything that happens after and subsequent calls to the function accumulates the effect. For example, calling `rotate_y(self.PI/2)` and then `rotate_y(self.PI/2)` is the same as `rotate_y(self.PI)`. If `rotate_y()` is called within the `draw()`, the transformation is reset when the loop begins again.

{# This function requires using P3D as a third parameter to size() as shown in the example above. #}

### Example

```py
self.size(400, 400)
self.translate(self.width / 2, self.height / 2)
self.rotate_y(self.PI/3.0)
self.rect(-104, -104, 208, 208)
```


```py
self.size(400, 400)
self.translate(self.width / 2, self.height / 2)
self.rotate_y(self.radians(60))
self.rect(-104, -104, 208, 208)
```

## Syntax

rotate_y(angle)

## Parameters

| Input | Description |
|-------|-------------|
| angle	(float) | the angle of rotation, specified in radians |

## Return

None

## Related

- [pop_matrix()](/docs/api/transform/pop_matrix_.md)
- [push_matrix()](/docs/api/transform/push_matrix_.md)
- [rotate()](/docs/api/transform/rotate_.md)
- [rotate_x()](/docs/api/transform/rotate_x_.md)
- [rotate_z()](/docs/api/transform/rotate_z_.md)
- [scale()](/docs/api/transform/scale_.md)
- [translate()](/docs/api/transform/translate_.md)