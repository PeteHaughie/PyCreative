[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[creating_and_reading](/docs/api/color/creating_and_reading/)→[saturation_.md](/docs/api/color/creating_and_reading/saturation_.md)

# saturation()

## Description

Extracts the saturation value from a color.

## Examples

```py
self.size(400, 400)
self.no_stroke()
self.color_mode(self.HSB, 255)
c = self.color(0, 126, 255)
self.fill(c)
self.rect(60, 80, 140, 240)
saturation_value = self.saturation(c)  # Get saturation in 'c'
self.println(saturation_value)  # Prints "255.0"
self.fill(saturation_value)
self.rect(200, 80, 140, 240)
```

## Syntax

saturation(c)

## Parameters

| Input | Description |
|-------|-------------|
| c (color | int) | a color value (returned by `color()` or an integer color value) |

## Range

Returned value is a float in the current color mode's scale (default HSB range 0–255 unless `color_mode()` is changed).

## Notes

Component values follow the current `color_mode()` scale. Use `color_mode()` to change numeric ranges.

## Return

float

## Related

- [red()](/docs/api/color/creating_and_reading/red_.md)
- [green()](/docs/api/color/creating_and_reading/green_.md)
- [blue()](/docs/api/color/creating_and_reading/blue_.md)
- [alpha()](/docs/api/color/creating_and_reading/alpha_.md)
- [hue()](/docs/api/color/creating_and_reading/hue_.md)
- [brightness()](/docs/api/color/creating_and_reading/brightness_.md)