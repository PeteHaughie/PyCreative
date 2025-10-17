[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[creating_and_reading](/docs/api/color/creating_and_reading/)→[color_.md](/docs/api/color/creating_and_reading/color_.md)

# color()

## Description

Creates colors for storing in variables of the color datatype. The parameters are interpreted as RGB or HSB values depending on the current `color_mode()`. The default mode is RGB values from 0 to 255 and, therefore, color(255, 204, 0) will return a bright yellow color (see the first example above).

Note that if only one value is provided to color(), it will be interpreted as a grayscale value. Add a second value, and it will be used for alpha transparency. When three values are specified, they are interpreted as either RGB or HSB values. Adding a fourth value applies alpha transparency.

Note that when using hexadecimal notation, it is not necessary to use color(), as in: color c = #006699

More about how colors are stored can be found in the reference for the color datatype.

## Examples

```py
self.size(400, 400)
self.no_stroke()
c = self.color(255, 204, 0)  # Define color 'c'
self.fill(c)  # Use color variable 'c' as fill color
self.rect(120, 80, 220, 220)  # Draw rectangle
```

```py
self.size(400, 400)
self.no_stroke()
c = self.color(255, 204, 0)  # Define color 'c'
self.fill(c)  # Use color variable 'c' as fill color
self.ellipse(100, 100, 320, 320)  # Draw left circle

# Using only one value with color()
# generates a grayscale value.
c = self.color(65)  # Update 'c' with grayscale value
self.fill(c)  # Use updated 'c' as fill color
self.ellipse(300, 300, 320, 320)  # Draw right circle
```

```py
self.size(400, 400)
self.no_stroke()

c = self.color(50, 55, 100)  # Create a color for 'c'
self.fill(c)  # Use color variable 'c' as fill color
self.rect(0, 40, 180, 320)  # Draw left rect

self.color_mode("HSB", 100)  # Use HSB with scale of 0-100
c = self.color(50, 55, 100)  # Update 'c' with new color
self.fill(c)  # Use updated 'c' as fill color
self.rect(220, 40, 180, 320)  # Draw right rect
```

## Syntax

color(gray)

color(gray, alpha)

color(v1, v2, v3)

color(v1, v2, v3, alpha)

## Notes

- `color(gray)` — grayscale value.
- `color(gray, alpha)` — grayscale with alpha.
- `color(v1, v2, v3)` — RGB or HSB depending on `color_mode()`.
- `color(v1, v2, v3, alpha)` — color with alpha transparency.

When using hexadecimal notation (e.g. `#006699`), you can usually use the literal in code without `color()` depending on language/context; in Python examples prefer `0x006699` or creating colors via `color()` for clarity.

## Parameters

| Input | Description |
|-------|-------------|
| gray (int  float) | grayscale value (0 = black, high = white) in the current color range |
| alpha (int  float) | alpha value (opacity) in the current color range |
| v1 (int  float) | red or hue value in the current color range |
| v2 (int  float) | green or saturation value in the current color range |
| v3 (int  float) | blue or brightness value in the current color range |

## Range

Component and alpha values follow the current `color_mode()` ranges. By default, RGB components and alpha use 0–255.

## Return

int (color value)

## Related

- [color_mode()](/docs/api/color/setting/color_mode_.md)