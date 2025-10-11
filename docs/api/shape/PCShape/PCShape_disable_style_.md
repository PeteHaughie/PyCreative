[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# disableStyle()

## Class

PCShape

## Description

Disables the shape's style data and uses PyCreative's current styles. Styles include attributes such as colors, stroke weight, and stroke joints.

## Examples

```py
def setup(self):
  self.size(400, 400)
  # The file "bot.svg" must be in the data folder
  # of the current sketch to load successfully
  self.s = self.load_shape("bot.svg")

def draw(self):
  self.s.disable_style()
  self.shape(self.s, -120, 40, 320, 320)
  self.s.enableStyle()
  self.shape(self.s, 200, 40, 320, 320)
```

## Syntax

sh.disable_style()

## Parameters

| Input | Description |
|-------|-------------|
| sh | (PCShape)	any variable of type PCShape |

## Return

pass

## Related

- [PCShape::enable_style()](/docs/api/shape/PCShape/PCShape_enable_style_.md)