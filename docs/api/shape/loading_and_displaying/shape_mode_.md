[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[loading and displaying](/docs/api/shape/loading_and_displaying/)

# shape_mode()

## Description

Modifies the location from which shapes draw. The default mode is `shape_mode("CORNER")`, which specifies the location to be the upper left corner of the shape and uses the third and fourth parameters of `shape()` to specify the width and height. The syntax `shape_mode("CORNERS")` uses the first and second parameters of `shape()` to set the location of one corner and uses the third and fourth parameters to set the opposite corner. The syntax `shape_mode("CENTER")` draws the shape from its center point and uses the third and forth parameters of `shape()` to specify the width and height. The parameter must be written in "ALL CAPS" because PyCreative is a case-sensitive language.

## Examples

```py
def setup(self):
  self.size(400, 400)
  self.bot = load_shape("bot.svg")

def draw(self):
  self.shape_mode("CENTER")
  self.shape(self.bot, 140, 140, 200, 200)
  self.shape_mode("CORNER")
  self.shape(self.bot, 140, 140, 200, 200)
```

## Syntax

shape_mode(mode)

## Parameters

| Input | Description |
|-------|-------------|
| mode (String) | either "CORNER", "CORNERS", "CENTER" |

## Return

None

## Related

- [PShape](/docs/api/shape/PCShape/PCShape.md)
- [shape()](/docs/api/shape/PCShape/PCShape_shape_.md)
- [rect_mode()](/docs/api/shape/attributes/rect_mode_.md)
