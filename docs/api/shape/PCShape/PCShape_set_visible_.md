[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# set_visible()

## Description

Sets the shape to be visible or invisible. This is determined by the value of the visible parameter.

The default visibility of a shape is usually controlled by whatever program created the SVG file.

## Examples

```py
def setup(self):
  self.size(400, 400);
  # The file "bot.svg" must be in the data folder
  # of the current sketch to load successfully
  self.s = self.load_shape("bot.svg")

def draw(self):
  self.background(204)
  self.shape(s, 40, 40, 320, 320)  # Draw shape

self.s.set_visible(mouse_pressed):
 if (s.is_visible() == false):  # Or use: "if (!s.is_visible)"
    self.no_fill()
    self.rect(40, 40, 320, 320)
```

## Syntax

sh.setVisible(visible)

## Parameters

| Input             | Description |
| ----------------- | ----------- |
| sh (PShape)       | any variable of type PShape |
| visible (boolean) | `False` makes the shape invisible and `True` makes it visible |

## Return

pass

## Related

[PCShape::is_visible()](/docs/api/shape/PCShape/PCShape_is_visible_.md)
