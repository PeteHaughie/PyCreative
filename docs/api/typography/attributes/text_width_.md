[docs](/docs/)→[api](/docs/api)→[typography](/docs/api/typography)→[attributes](/docs/api/typography/attributes)→[text_width()](/docs/api/typography/attributes/text_width_.md)

# text_width()

## Description

Calculates and returns the width of any character or text string.

## Examples

```py
"""
size(400, 400);
textSize(112);

char c = 'T';
float cw = textWidth(c);
text(c, 0, 160);
line(cw, 0, cw, 200); 

String s = "Tokyo";
float sw = textWidth(s);
text(s, 0, 340);
line(sw, 200, sw, 400);
"""
```

## Syntax

textWidth(c)

textWidth(str)

## Parameters

| Input | Description |
|-------|-------------|
| c	(char) | the character to measure |
| str	(String) | the String of characters to measure |

## Return

float	

## Related

- [load_font()](/docs/api/typography/loading_and_displaying/load_font_.md)
- [text()](/docs/api/typography/loading_and_displaying/text_.md)
- [text_font()](/docs/api/typography/loading_and_displaying/text_font_.md)
- [text_size()](/docs/api/typography/attributes/text_size_.md)