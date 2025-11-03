[docs](/docs/)→[api](/docs/api)→[typography](/docs/api/typography)→[PCFont](/docs/api/typography/PCFont/PCFont.md)

# PCFont

## Description

PCFont is the font class for PyCreative. The `load_font()` function constructs a new font and `text_font()` makes a font active. The `list()` method creates a list of the fonts installed on the computer.

## Examples

```py
def setup(self):
    self.size(400, 400)
    # The font can be located in the sketch's 
    # "data" directory or in the system fonts folder
    # use the PCFont::list method to see available fonts
    self.font = self.load_font("LetterGothicStd.otf", 128)
    self.text_font(self.font)
    self.text("word", 50, 200)
```

## Methods

list()	Gets a list of the fonts installed on the system

## Related

- [load_font()](/docs/api/typography/loading_and_displaying/load_font_.md)
- [PCFont::list()](/docs/api/typography/PCFont/PCFont_list_.md)