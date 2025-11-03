[docs](/docs/)→[api](/docs/api)→[typography](/docs/api/typography)→[text_font()](/docs/api/typography/loading_and_displaying/text_font_.md)

# text_font()

## Description

Sets the current font that will be drawn with the `text()` function. Fonts must be created for Processing with createFont() or loaded with `load_font()` before they can be used. The font set through textFont() will be used in all subsequent calls to the `text()` function. 

## Examples

```py
def setup(self):
    self.size(400,400)
    # The font "andalemo.ttf" must be located in the 
    # current sketch's "data" directory to load successfully
    self.mono = self.load_font("andalemo.ttf", 128)
    self.background(0)
    self.text_font(self.mono)
    self.text("word", 48, 240)
```

## Syntax

.text_font(font)

.text_font(font, size)

## Parameters

| Input | Description |
|-------|-------------|
| font (PCFont) | The font to be used for rendering text. |
| size (float) | The size of the font in units of pixels. |

## Return

None

## Related

- [load_font()](/docs/api/typography/loading_and_displaying/load_font_.md)
- [PCFont](/docs/api/typography/PCFont/PCFont.md)
- [text()](/docs/api/typography/loading_and_displaying/text_.md)
- [text_size()](/docs/api/typography/loading_and_displaying/text_size_.md)
