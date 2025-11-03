[docs](/docs/)→[api](/docs/api)→[typography](/docs/api/typography)→[PCFont](/docs/api/typography/PCFont)→[PCFont::list()](/docs/api/typography/PCFont/PCFont_list_.md)

# list()

## Class
 PCFont

## Description

Gets a list of the fonts installed on the system. The data is returned as a `String` array. This list provides the names of each font for input into createFont(), which allows PyCreative to dynamically format fonts.

## Examples
```py
def setup(self):
    self.size(200, 200)
    font_list = self.PFont.list()
    self.print_array(font_list)
```

## Syntax

.list()	

## Return

String[]	