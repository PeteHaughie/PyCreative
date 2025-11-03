[docs](/docs/)→[api](/docs/api)→[typography](/docs/api/typography)→[loading_and_displaying](/docs/api/typography/loading_and_displaying)→[text()](/docs/api/typography/loading_and_displaying/text_.md)

# text()

## Description

Draws text to the screen. Displays the information specified in the first parameter on the screen in the position specified by the additional parameters. A default font will be used unless a font is set with the `text_font()` function and a default size will be used unless a font is set with `text_size()`. Change the color of the text with the `fill()` function. The text displays in relation to the `text_align()` function, which gives the option to draw to the left, right, and center of the coordinates.

The x2 and y2 parameters define a rectangular area to display within and may only be used with string data. When these parameters are specified, they are interpreted based on the current `rect_mode()` setting. Text that does not fit completely within the rectangle specified will not be drawn to the screen.

Note that PyCreative now lets you call `text()` without first specifying a PCFont with `text_font()`. In that case, a generic sans-serif font will be used instead.

## Examples

```py
def setup(self):
    self.size(400, 400)
    self.text_size(128)
    self.text("word", 40, 120)
    self.fill(0, 408, 612)
    self.text("word", 40, 240)
    self.fill(0, 408, 612, 204)
    self.text("word", 40, 360)
```

```py
def setup(self):
    self.size(400, 400)
    s = "The quick brown fox jumps over the lazy dog."
    self.fill(200)
    self.text(s, 40, 40, 280, 320)  # Text wraps within text box
```

## Syntax

text(c, x, y)

text(c, x, y, z)

text(str, x, y)

text(chars, start, stop, x, y)

text(str, x, y, z)

text(chars, start, stop, x, y, z)

text(str, x1, y1, x2, y2)

text(num, x, y)

text(num, x, y, z)

## Parameters

| Input | Description |
|-------|-------------|
| c	(char) | the alphanumeric character to be displayed |
| x	(float) | x-coordinate of text |
| y	(float) | y-coordinate of text |
| z	(float) | z-coordinate of text |
| chars	(char[]) | the alphanumeric symbols to be displayed |
| start	(int) | array index at which to start writing characters |
| stop	(int) | array index at which to stop writing characters |
| x1	(float) | by default, the x-coordinate of text, see rectMode() for more info |
| y1	(float) | by default, the y-coordinate of text, see rectMode() for more info |
| x2	(float) | by default, the width of the text box, see rectMode() for more info |
| y2	(float) | by default, the height of the text box, see rectMode() for more info |
| num	(float, int) | the numeric value to be displayed |

## Return

None	

## Related

- [text_align()](/docs/api/typography/loading_and_displaying/text_align_.md)
- [text_font()](/docs/api/typography/loading_and_displaying/text_font_.md)
- [text_size()](/docs/api/typography/attributes/text_size_.md)
- [text_leading()](/docs/api/typography/attributes/text_leading_.md)
- [text_width()](/docs/api/typography/attributes/text_width_.md)
- [text_ascent()](/docs/api/typography/metrics/text_ascent_.md)
- [text_descent()](/docs/api/typography/metrics/text_descent_.md)
- [rect_mode()](/docs/api/shapes/rect_mode_.md)
- [fill()](/docs/api/color/fill_.md)
- [String()](/docs/api/data/composite/string.md)
