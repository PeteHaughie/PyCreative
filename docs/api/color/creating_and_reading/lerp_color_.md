[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[creating_and_reading](/docs/api/color/creating_and_reading/)→[lerp_color_.md](/docs/api/color/creating_and_reading/lerp_color_.md)

# lerpColor()

## Description

Calculates a color between two colors at a specific increment. The amt parameter is the amount to interpolate between the two values where 0.0 is equal to the first point, 0.1 is very near the first point, 0.5 is halfway in between, etc.

An amount below 0 will be treated as 0. Likewise, amounts above 1 will be capped at 1. This is different from the behavior of `lerp()`, but necessary because otherwise numbers outside the range will produce strange and unexpected colors.

## Examples

```py
self.size(400, 400)
self.background(51)
self.stroke(255)
from_color = self.color(204, 102, 0)
to_color = self.color(0, 102, 153)
inter_a = self.lerp_color(from_color, to_color, 0.33)
inter_b = self.lerp_color(from_color, to_color, 0.66)
self.fill(from_color)
self.rect(40, 80, 80, 240)
self.fill(inter_a)
self.rect(120, 80, 80, 240)
self.fill(inter_b)
self.rect(200, 80, 80, 240)
self.fill(to_color)
self.rect(280, 80, 80, 240)
```

## Syntax

lerp_color(c1, c2, amt)

## Parameters

| Input | Description |
|-------|-------------|
| c1 (color | int) | starting color |
| c2 (color | int) | ending color |
| amt (float) | interpolation amount; values are clamped to [0.0, 1.0] |

## Return

int (color value)

## Related

- [PCImage::blend_color()](/docs/api/image/processing/PCImage/blend_color_.md)
- [color()](/docs/api/color/creating_and_reading/color_.md)
- [lerp()](/docs/api/color/creating_and_reading/lerp_.md)