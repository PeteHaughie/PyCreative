[docs](/docs/)→[api](/docs/api)→[rendering](/docs/api/rendering)→[blend_mode()](/docs/api/rendering/blend_mode_.md)

# blend_mode()

## Description

Blends the pixels in the display window according to a defined mode. There is a choice of the following modes to blend the source pixels (A) with the ones of pixels already in the display window (B). Each pixel's final color is the result of applying one of the blend modes with each channel of (A) and (B) independently. The red channel is compared with red, green with green, and blue with blue.

"BLEND" - linear interpolation of colors: C = A*factor + B. This is the default.

"ADD" - additive blending with white clip: C = min(A*factor + B, 255)

"SUBTRACT" - subtractive blending with black clip: C = max(B - A*factor, 0)

"DARKEST" - only the darkest color succeeds: C = min(A*factor, B)

"LIGHTEST" - only the lightest color succeeds: C = max(A*factor, B)

"DIFFERENCE" - subtract colors from underlying image.

"EXCLUSION" - similar to DIFFERENCE, but less extreme.

"MULTIPLY" - multiply the colors, result will always be darker.

"SCREEN" - opposite multiply, uses inverse values of the colors.

"REPLACE" - the pixels entirely replace the others and don't utilize alpha (transparency) values

## Examples

```py
def setup(self):
    self.size(100, 100)
    self.background(0)
    self.blend_mode("ADD")
    self.stroke(102)
    self.stroke_weight(30)
    self.line(25, 25, 75, 75)
    self.line(75, 25, 25, 75)
```

```py
def setup(self):
    self.size(100, 100)
    self.blend_mode("MULTIPLY")
    self.stroke(51)
    self.stroke_weight(30)
    self.line(25, 25, 75, 75)
    self.line(75, 25, 25, 75)
```

## Syntax

blend_mode(mode)

## Parameters

| Input | Description |
|-------|-------------|
| mode	(String) | the blending mode to use |

## Return

None

## Related

- [blend()](/docs/api/image/pixels/blend_.md)