[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[creating_and_reading](/docs/api/color/creating_and_reading/)→[alpha_.md](/docs/api/color/creating_and_reading/alpha_.md)

# alpha()

## Description

Extracts the alpha value from a color.

## Examples

```py
self.size(400, 400)
self.no_stroke()
c = self.color(0, 126, 255, 102)
self.fill(c)
self.rect(60, 60, 140, 280)
alpha_value = self.alpha(c)  # Sets 'alpha_value' to 102.0
self.fill(alpha_value)
self.rect(200, 60, 140, 280)
```

## Syntax

alpha(c)

## Parameters

| Input | Description |
|-------|-------------|
| c (color | int) | a color value (returned by `color()` or an integer color value) |

## Range

Returned alpha is a float in the current color mode's scale (default RGB alpha range 0–255).

## Notes

Component values follow the current `color_mode()` scale. Use `color_mode()` to change numeric ranges.

## Return

float

## Related

- [red()](/docs/api/color/creating_and_reading/red_.md)
- [green()](/docs/api/color/creating_and_reading/green_.md)
- [blue()](/docs/api/color/creating_and_reading/blue_.md)
- [hue()](/docs/api/color/creating_and_reading/hue_.md)
- [saturation()](/docs/api/color/creating_and_reading/saturation_.md)
- [brightness()](/docs/api/color/creating_and_reading/brightness_.md)