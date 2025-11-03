[docs](/docs/)→[api](/docs/api)→[typography](/docs/api/typography)→[attributes](/docs/api/typography/attributes)→[text_align_.md](/docs/api/typography/attributes/text_align_.md)

# text_align()

## Description

Sets the current alignment for drawing text. The parameters "LEFT", "CENTER", and "RIGHT" set the display characteristics of the letters in relation to the values for the x and y parameters of the `text()` function.

An optional second parameter can be used to vertically align the text. "BASELINE" is the default, and the vertical alignment will be reset to "BASELINE" if the second parameter is not used. The "TOP" and "CENTER" parameters are straightforward. The "BOTTOM" parameter offsets the line based on the current `text_descent()`. For multiple lines, the final line will be aligned to the bottom, with the previous lines appearing above it.

When using `text()` with width and height parameters, "BASELINE" is ignored, and treated as "TOP". (Otherwise, text would by default draw outside the box, since "BASELINE" is the default setting. "BASELINE" is not a useful drawing mode for text drawn in a rectangle.)

The vertical alignment is based on the value of `text_ascent()`, which many fonts do not specify correctly. It may be necessary to use a hack and offset by a few pixels by hand so that the offset looks correct. To do this as less of a hack, use some percentage of `text_ascent()` or `text_descent()` so that the hack works even if you change the size of the font.

## Examples

```py
def setup(self):
    self.size(400, 400)
    self.background(0)
    self.text_size(64)
    self.text_align(self.RIGHT)
    self.text("ABCD", 200, 120)
    self.text_align(self.CENTER)
    self.text("EFGH", 200, 200)
    self.text_align(self.LEFT)
    self.text("IJKL", 200, 280)
```

```py
def setup(self):
    self.size(400, 400)
    self.background(0)
    self.stroke(153)
    self.text_size(44)
    self.text_align(self.CENTER, self.BOTTOM)
    self.line(0, 120, self.width, 120)
    self.text("CENTER,BOTTOM", 200, 120)
    self.text_align(self.CENTER, self.CENTER)
    self.line(0, 200, self.width, 200)
    self.text("CENTER,CENTER", 200, 200)
    self.text_align(self.CENTER, self.TOP)
    self.line(0, 280, self.width, 280)
    self.text("CENTER,TOP", 200, 280)
```

## Syntax

text_align(alignX)

text_align(alignX, alignY)

## Parameters

| Input | Description |
|-------|-------------|
| alignX	(String) | horizontal alignment, either "LEFT", "CENTER", or "RIGHT" |
| alignY	(String) | vertical alignment, either "TOP", "BOTTOM", "CENTER", or "BASELINE" |

## Return

None	

## Related

- [load_font()](/docs/api/typography/loading_and_displaying/load_font_.md)
- [PCFont](/docs/api/typography/PCFont/PCFont.md)
- [text()](/docs/api/typography/loading_and_displaying/text_.md)
- [text_size()](/docs/api/typography/attributes/text_size_.md)
- [text_ascent()](/docs/api/typography/metrics/text_ascent_.md)
- [text_descent()](/docs/api/typography/metrics/text_descent_.md)