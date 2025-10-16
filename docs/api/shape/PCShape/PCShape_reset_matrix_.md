[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# reset_matrix()

## Class

PCShape

## Description

Replaces the current matrix of a shape with the identity matrix. The equivalent function in OpenGL is `glLoadIdentity()`.

## Examples

```py
def setup(self):
  self.size(100, 100)
  self.s = load_shape("ohio.svg")
  self.s.rotate(self.PI/6)

def draw(self):
  self.background(204)
  self.shape(self.s)

def mouse_pressed(self):
  # Removes all transformations applied to shape
  # Loads the identity matrix
  self.s.reset_matrix()
```

## Syntax

sh.reset_matrix()

## Parameters

sh	(PCShape)	any variable of type PCShape

## Return

None

## Related

- [PCShape::rotate()](/docs/api/shape/PCShape/PCShape_rotate_.md)
- [PCShape::scale()](/docs/api/shape/PCShape/PCShape_scale_.md)
- [PCShape::translate()](/docs/api/shape/PCShape/PCShape_translate_.md)