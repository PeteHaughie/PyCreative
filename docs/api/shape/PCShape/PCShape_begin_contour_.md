[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# begin_contour()

## Class

PCShape

## Description

The `begin_contour()` and `end_contour()` methods make it possible to define shapes with other shapes cut out of them. For example, the inside of a letter 'O'. These two functions are always used together, you'll never use one without the other. Between them, define the geometry you want to create.

The exterior shape and the interior contour must wind in opposite directions. This means that if the points of the geometry for the exterior shape are described in a clockwise order, the points on the interior shape are defined in a counterclockwise order.

## Examples

```py
def setup(self):
  self.size(200, 200)

  # Make a shape
  self.s = self.create_shape()
  self.s.begin_shape()
  # self.s.noStroke()

  # Exterior part of shape
  self.s.vertex(-50, -50)
  self.s.vertex(50, -50)
  self.s.vertex(50, 50)
  self.s.vertex(-50, 50)

  # Interior part of shape
  self.s.begin_contour()
  self.s.vertex(-20, -20)
  self.s.vertex(-20, 20)
  self.s.vertex(20, 20)
  self.s.vertex(20, -20)
  self.s.end_contour()

  # Finish off shape
  self.s.end_shape(CLOSE)

def draw(self):
  self.background(204)
  self.translate(self.width/2, self.height/2)
  self.s.rotate(0.01)
  self.shape(self.s)
```

## Syntax

sh.begin_contour()

## Parameters

| Input | Description |
|-------|-------------|
| sh	(PCShape) | any variable of type PCShape |

## Return

pass

## Related

- [PShape::end_contour()](/docs/api/shape/PCShape/PCShape_end_contour_.md)