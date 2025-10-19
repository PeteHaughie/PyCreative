[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[attributes](/docs/api/shape/attributes/)→[stroke_weight()](/docs/api/shape/attributes/stroke_weight_/)

# stroke_weight()

## Description

Sets the width of the stroke used for lines, points, and the border around shapes. All widths are set in units of pixels.

Using `point()` with `stroke_weight(1)` or smaller may draw nothing to the screen, depending on the graphics settings of the computer. Workarounds include setting the pixel using `set()` or drawing the point using either `circle()` or `square()`.

## Examples

```py
"""
size(400, 400);
strokeWeight(4);  // Default
line(80, 80, 320, 80);
strokeWeight(16);  // Thicker
line(80, 160, 320, 160);
strokeWeight(40);  // Beastly
line(80, 280, 320, 280);
"""
```

## Syntax

stroke_weight(weight)

## Parameters

| Inputs | Description |
|--------|-------------|
| weight (float) | the weight (in pixels) of the stroke |

## Return

None

## Related

- [stroke()](/docs/api/color/setting/stroke_.md)
- [stroke_join()](/docs/api/shape/attributes/stroke_join_.md)
- [stroke_cap()](/docs/api/shape/attributes/stroke_cap_.md)