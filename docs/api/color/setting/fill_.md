[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[setting](/docs/api/setting/)

# fill()

## Description

Sets the color used to fill shapes. For example, if you run fill(204, 102, 0), all subsequent shapes will be filled with orange. This color is either specified in terms of the RGB or HSB color depending on the current `color_mode()` (the default color space is RGB, with each value in the range from 0 to 255).

When using hexadecimal notation to specify a color, use "#" or "0x" before the values (e.g. #CCFFAA, 0xFFCCFFAA). The # syntax uses six digits to specify a color (the way colors are specified in HTML and CSS). When using the hexadecimal notation starting with "0x", the hexadecimal value must be specified with eight characters; the first two characters define the alpha component and the remainder the red, green, and blue components.

The value for the parameter "gray" must be less than or equal to the current maximum value as specified by `color_mode()`. The default maximum value is 255.

To change the color of an image (or a texture), use `tint()`.

## Examples

```py
self.size(400, 400)
self.fill(153)  # Set fill to gray
self.rect(120, 80, 220, 220)  # Draw rect with gray fill
```

```py
self.size(400, 400)
self.fill(204, 102, 0)
self.rect(120, 80, 220, 220)
```

## Syntax

fill(rgb)

fill(rgb, alpha)

fill(gray)

fill(gray, alpha)

fill(v1, v2, v3)

fill(v1, v2, v3, alpha)

## Parameters

| Input | Description |
|-------|-------------|
| rgb	(int) | color variable or hex value |
| alpha	(float)	| opacity of the fill |
| gray	(float)	| number specifying value between white and black |
| v1	(float)	| red or hue value (depending on current color mode) |
| v2	(float)	| green or saturation value (depending on current color mode) |
| v3	(float)	| blue or brightness value (depending on current color mode) |

## Return

pass

## Related

- [no_fill()](/docs/api/color/setting/no_fill_.md)
- [stroke()](/docs/api/color/setting/stroke_.md)
- [no_stroke()](/docs/api/color/setting/no_stroke_.md)
- [tint()](/docs/api/color/setting/tint_.md)
- [background()](/docs/api/color/setting/background_.md)
- [color_mode()](/docs/api/color/setting/color_mode_.md)