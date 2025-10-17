[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[setting](/docs/api/setting/)→[no_fill_.md](/docs/api/color/setting/no_fill_.md)

# no_fill()

## Description

Disables filling geometry. If both `no_stroke()` and `no_fill()` are called, nothing will be drawn to the screen.

## Examples

```py
self.size(400, 400)
self.rect(60, 40, 220, 220)
self.no_fill()  # Disable filling geometry
self.rect(120, 80, 220, 220)  # Draw rect with no fill
```

## Syntax

no_fill()

## Return

None

## Related

- [fill()](/docs/api/color/setting/fill_.md)
- [stroke()](/docs/api/color/setting/stroke_.md)
- [no_stroke()](/docs/api/color/setting/no_stroke_.md)