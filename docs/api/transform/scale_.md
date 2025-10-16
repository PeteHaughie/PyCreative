[docs](/docs/)→[api](/docs/api)→[transform](/docs/api/transform/)→[scale()](/docs/api/transform/scale_.md)

# scale()

## Description

Increases or decreases the size of a shape by expanding and contracting vertices. Objects always scale from their relative origin to the coordinate system. Scale values are specified as decimal percentages. For example, the function call `scale(2.0)` increases the dimension of a shape by 200%.

Transformations apply to everything that happens after and subsequent calls to the function multiply the effect. For example, calling `scale(2.0)` and then `scale(1.5)` is the same as `scale(3.0)`. If `scale()` is called within `draw()`, the transformation is reset when the loop begins again. Using this function with the z parameter requires using P3D as a parameter for `size()`, as shown in the third example above. This function can be further controlled with `push_matrix()` and `pop_matrix()`.

## Example

```py
self.size(400, 400)
self.rect(120, 80, 200, 200)
self.scale(0.5)
self.rect(120, 80, 200, 200)
```

```py
self.size(400, 400)
self.rect(120, 80, 200, 200)
self.scale(0.5, 1.3)
self.rect(120, 80, 200, 200)
```

```py
self.size(400, 400)
self.no_fill()
self.translate(self.width/2+48, self.height/2)
self.box(80, 80, 80)
self.scale(2.5, 2.5, 2.5)
self.box(80, 80, 80)
```

## Syntax

scale(s)

scale(sx, sy)

scale(sx, sy, sz)

## Parameters

| Input | Description |
|-------|-------------|
| s (float) | uniform scale factor in all dimensions |
| sx (float) | scale factor in x dimension |
| sy (float) | scale factor in y dimension |
| sz (float) | scale factor in z dimension |

## Return

None

## Related

- [push_matrix()](/docs/api/transform/push_matrix_.md)
- [pop_matrix()](/docs/api/transform/pop_matrix_.md)
- [translate()](/docs/api/transform/translate_.md)
- [rotate()](/docs/api/transform/rotate_.md)
- [rotate_x()](/docs/api/transform/rotate_x_.md)
- [rotate_y()](/docs/api/transform/rotate_y_.md)
- [rotate_z()](/docs/api/transform/rotate_z_.md)