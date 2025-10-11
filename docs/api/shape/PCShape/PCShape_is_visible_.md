[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# is_visible()

## Description

Returns a boolean value true if the image is set to be visible, false if not. This value can be modified with the `set_visible()` method.

## Examples

```py
def setup(self):
  self.size(400, 400)
  # The file "bot.svg" must be in the data folder
  # of the current sketch to load successfully
  self.s = self.load_shape("bot.svg")

def draw(self):
  self.background(204)
  self.shape(self.s, 40, 40, 320, 320)  # Draw shape

self.s.set_visible(mouse_pressed)
  if (self.s.is_visible() == false):  # Or use: "if (!self.s.is_visible)"
    self.no_fill()
    self.rect(40, 40, 320, 320)
```

## Syntax

sh.is_visible()	

## Parameters

sh	(PCShape)	any variable of type PCShape

## Return

boolean	

## Related
- [PCShape::set_visible()](/docs/api/shape/PCShape/PCShape_set_visible_.md)
