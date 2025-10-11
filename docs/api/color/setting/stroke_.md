[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[setting](/docs/api/setting/)

# stroke()

## Description

Sets the color used to draw lines and borders around shapes. This color is either specified in terms of the RGB or HSB color depending on the current `color_mode()`. The default color space is RGB, with each value in the range from 0 to 255.

When using hexadecimal notation to specify a color, use "#" or "0x" before the values (e.g., #CCFFAA or 0xFFCCFFAA). The # syntax uses six digits to specify a color (just as colors are typically specified in HTML and CSS). When using the hexadecimal notation starting with "0x", the hexadecimal value must be specified with eight characters; the first two characters define the alpha component, and the remainder define the red, green, and blue components.

The value for the gray parameter must be less than or equal to the current maximum value as specified by `color_mode()`. The default maximum value is 255.

## Examples

```py
self.size(400, 400)
self.stroke(153)  # Set stroke to gray
self.rect(120, 80, 220, 220)  # Draw rect with gray stroke
```

```py
self.size(400, 400)
self.stroke(204, 102, 0)
self.rect(120, 80, 220, 220)
```

## Syntax

stroke(rgb)

stroke(rgb, alpha)

stroke(gray)

stroke(gray, alpha)

stroke(v1, v2, v3)

stroke(v1, v2, v3, alpha)

## Parameters

| Input | Description |
|-------|-------------|
| rgb	(int) | color value in hexadecimal notation |
| alpha	(float) | opacity of the stroke |
| gray	(float) | specifies a value between white and black |
| v1	(float) | red or hue value (depending on current color mode) |
| v2	(float) | green or saturation value (depending on current color mode) |
| v3	(float) | blue or brightness value (depending on current color mode) |

## Return

pass

## Related

[no_stroke()](/docs/api/color/setting/no_stroke_.md)
[stroke_weight()](/docs/api/color/setting/stroke_weight_.md)
[stroke_join()](/docs/api/color/setting/stroke_join_.md)
[stroke_cap()](/docs/api/color/setting/stroke_cap_.md)
[fill()](/docs/api/color/setting/fill_.md)
[no_fill()](/docs/api/color/setting/no_fill_.md)
[tint()](/docs/api/color/setting/tint_.md)
[background()](/docs/api/color/setting/background_.md)
[color_mode()](/docs/api/color/setting/color_mode_.md)