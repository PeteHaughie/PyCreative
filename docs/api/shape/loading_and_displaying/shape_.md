[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[loading and displaying](/docs/api/shape/loading_and_displaying/)

# shape()

## Description

Draws shapes to the display window. Shapes must be in the sketch's "data" directory to load correctly. Select "Add file..." from the "Sketch" menu to add the shape. PyCreative currently works with SVG, OBJ, and custom-created shapes. The shape parameter specifies the shape to display and the coordinate parameters define the location of the shape from its upper-left corner. The shape is displayed at its original size unless the `c` and `d` parameters specify a different size. The `shape_mode()` function can be used to change the way these parameters are interpreted.

## Examples

```py
def setup(self):
  self.size(400,400)
  self.s = self.load_shape("bot.svg")

def draw(self):
  self.shape(self.s, 40, 40, 320, 320)
```

## Syntax

shape(shape)

shape(shape, x, y)	

shape(shape, a, b, c, d)	

## Parameters

| Input | Description |
|-------|-------------|
|shape	(PCShape) | the shape to display |
|x	(float) | x-coordinate of the shape |
|y	(float) | y-coordinate of the shape |
|a	(float) | x-coordinate of the shape |
|b	(float) | y-coordinate of the shape |
|c	(float) | width to display the shape |
|d	(float) | height to display the shape |

## Return

None

## Related
- [PCShape](/docs/api/shape/PCShape/PCShape.md)
- [load_shape()](/docs/api/shape/loading_and_displaying/load_shape_.md)
- [shape_mode()](/docs/api/shape/loading_and_displaying/shape_mode_.md)