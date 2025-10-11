[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[setting](/docs/api/setting/)

# no_stroke()

## Description

Disables drawing the stroke (outline). If both `no_stroke()` and `no_fill()` are called, nothing will be drawn to the screen.

## Examples

```py
self.size(400, 400)
self.no_stroke()  # Disable drawing the stroke (outline)
self.rect(120, 80, 220, 220)  # Draw rect with no stroke
```

## Syntax

no_stroke()

## Return

pass

## Related

- [stroke()](/docs/api/color/setting/stroke_.md)
- [fill()](/docs/api/color/setting/fill_.md)
- [no_fill()](/docs/api/color/setting/no_fill_.md)