[docs](/docs/)→[api](/docs/api)→[typography](/docs/api/typography)→[attributes](/docs/api/typography/attributes)→[text_leading()](/docs/api/typography/attributes/text_leading_.md)

# text_leading()

## Description

Sets the spacing between lines of text in units of pixels. This setting will be used in all subsequent calls to the `text()` function. Note, however, that the leading is reset by `text_size()`. For example, if the leading is set to 20 with `text_leading(20)`, then if `text_size(48)` is run at a later point, the leading will be reset to the default for the text size of 48.

## Examples

```py
"""
size(400, 400);

// Text to display. The "\n" is a "new line" character
String lines = "L1\nL2\nL3";
textSize(48);
fill(0);  // Set fill to black

textLeading(40);  // Set leading to 40
text(lines, 40, 100);

textLeading(80);  // Set leading to 80
text(lines, 160, 100);

textLeading(120);  // Set leading to 120
text(lines, 280, 100);
"""
def setup(self):
    self.size(400, 400)
    lines = "L1\nL2\nL3"
    self.text_size(48)
    self.fill(0)  # Set fill to black

    self.text_leading(40)  # Set leading to 40
    self.text(lines, 40, 100)

    self.text_leading(80)  # Set leading to 80
    self.text(lines, 160, 100)

    self.text_leading(120)  # Set leading to 120
    self.text(lines, 280, 100)
```

## Syntax

text_leading(leading)

## Parameters

| Input | Description |
|-------|-------------|
| leading	(float) | the size in pixels for spacing between lines |

## Return

None

## Related

- [load_font()](/docs/api/typography/loading_and_displaying/load_font_.md)
- [text()](/docs/api/typography/loading_and_displaying/text_.md)
- [text_font()](/docs/api/typography/attributes/text_font_.md)
- [text_size()](/docs/api/typography/attributes/text_size_.md)