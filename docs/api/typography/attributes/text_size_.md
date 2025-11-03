[docs](/docs/)→[api](/docs/api)→[typography](/docs/api/typography)→[attributes](/docs/api/typography/attributes)→[text_size()](/docs/api/typography/attributes/text_size_.md)

# text_size()

## Description

Sets the current font size. This size will be used in all subsequent calls to the `text()` function. Font size is measured in units of pixels.

## Examples
```py
def setup(self):
    self.size(400, 400)
    self.background(0)
    self.fill(255)
    self.text_size(104)
    self.text("WORD", 40, 200)
    self.text_size(56)
    self.text("WORD", 40, 280)
```

## Syntax

text_size(size)

## Parameters

| Input | Description |
|-------|-------------|
| size	(float)	| the size of the letters in units of pixels |

## Return

None

## Related

- [load_font()](/docs/api/typography/loading_and_displaying/load_font_.md)
- [text()](/docs/api/typography/loading_and_displaying/text_.md)
- [text_font()](/docs/api/typography/loading_and_displaying/text_font_.md)