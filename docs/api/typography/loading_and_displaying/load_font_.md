[docs](/docs/)→[api](/docs/api)→[typography](/docs/api/typography)→[load_font()](/docs/api/typography/loading_and_displaying/load_font_.md)

# load_font()

## Description

Like `load_image()` and other functions that load data, the `load_font()` function should not be used inside `draw()`, because it will slow down the sketch considerably, as the font will be re-loaded from the disk (or network) on each frame. It's recommended to load files inside `setup()`.

To load correctly, fonts must be located in the "data" folder of the current sketch. Alternatively, the file maybe be loaded from anywhere on the local computer using an absolute path (something that starts with / on Unix and Linux, or a drive letter on Windows), or the filename parameter can be a URL for a file found on a network.

## Examples

```py
"""
size(400, 400);
PFont font;
// The font must be located in the sketch's 
// "data" directory to load successfully
font = loadFont("LetterGothicStd.otf");
textFont(font, 128);
text("word", 50, 200);
"""
def setup(self):
    self.size(400, 400)
    # The font must be located in the sketch's 
    # "data" directory to load successfully
    self.font = self.load_font("LetterGothicStd.otf")
    self.text_font(self.font, 128)
    self.text("word", 50, 200)
```

## Syntax

.load_font(filename)

## Parameters

| Input | Description |
|-------|-------------|
| filename (String) | The name of the font file to load. |

## Return

PCFont

## Related

- [PCFont](/docs/api/typography/PCFont/PCFont.md)
- [text_font()](/docs/api/typography/loading_and_displaying/text_font_.md)