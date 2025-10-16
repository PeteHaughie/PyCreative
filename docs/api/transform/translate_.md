[docs](/docs/)→[api](/docs/api)→[transform](/docs/api/transform/)→[translate()](/docs/api/transform/translate_.md)

# translate()

## Description

Specifies an amount to displace objects within the display window. The `x` parameter specifies left/right translation, the `y` parameter specifies up/down translation, and the `z` parameter specifies translations toward/away from the screen.

Transformations are cumulative and apply to everything that happens after and subsequent calls to the function accumulates the effect. For example, calling `translate(50, 0)` and then `translate(20, 0)` is the same as `translate(70, 0)`. If `translate()` is called within `draw()`, the transformation is reset when the loop begins again. This function can be further controlled by using `push_matrix()` and `pop_matrix()`.

## Example

```py
self.size(400, 400)
self.translate(120, 80)
self.rect(0, 0, 220, 220)
```

```py
self.size(400, 400)
self.translate(120, 80, -200)
self.rect(0, 0, 220, 220)
``` 

```py
self.size(400, 400)
self.rect(0, 0, 220, 220)  # Draw rect at original 0,0
self.translate(120, 80)
self.rect(0, 0, 220, 220)  # Draw rect at new 0,0
self.translate(56, 56)
self.rect(0, 0, 220, 220)  # Draw rect at new 0,0
```

## Syntax

translate(x, y)

translate(x, y, z)

## Parameters

| Input | Description |
|-------|-------------|
| x (float) | distance to translate in x dimension |
| y (float) | distance to translate in y dimension |
| z (float) | distance to translate in z dimension |

## Return

None

## Related

- [pop_matrix()](/docs/api/transform/pop_matrix_.md)
- [push_matrix()](/docs/api/transform/push_matrix_.md)
- [rotate()](/docs/api/transform/rotate_.md)
- [rotate_x()](/docs/api/transform/rotate_x_.md)
- [rotate_y()](/docs/api/transform/rotate_y_.md)
- [rotate_z()](/docs/api/transform/rotate_z_.md)
- [scale()](/docs/api/transform/scale_.md)