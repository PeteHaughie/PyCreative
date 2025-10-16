[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# enable_style()

## Class

PCShape

## Description

Enables the shape's style data and ignores PyCreative's current styles. Styles include attributes such as colors, stroke weight, and stroke joints.

## Example

```py
def setup():
  self.size(400, 400)
  # The file "bot.svg" must be in the data folder
  # of the current sketch to load successfully
  self.s = load_shape("bot.svg")

def draw(self):
  self.s.disable_style()
  self.shape(self.s, -120, 40, 320, 320)
  self.s.enable_style()
  self.shape(self.s, 200, 40, 320, 320)
```

## Syntax

sh.enable_style()	

## Parameters

| Input | Description |
|-------|-------------|
| sh	(PCShape) | any variable of type PCShape |

## Return

None

## Related

- [PCShape::disable_style()](/docs/api/shape/PCShape/PCShape_disable_style_.md)