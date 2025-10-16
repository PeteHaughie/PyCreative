[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# add_child()

## Class

PShape

## Description

Adds a child PCShape to a parent PCShape that is defined as a GROUP. In the example, the three shapes path, rectangle, and circle are added to a parent PCShape variable named house that is a GROUP.

## Examples

```py
def setup(self):
  self.size(200, 200)

  # Make a group PShape
  self.house = self.create_shape("GROUP")
  
  # Make three shapes
  path = self.create_shape()
  path.begin_shape()
  path.vertex(-20, -20)
  path.vertex(0, -40)
  path.vertex(20, -20)
  path.end_shape()
  rectangle = self.create_shape("RECT", -20, -20, 40, 40)
  circle = self.create_shape("ELLIPSE", 0, 0, 20, 20)
  
  # Add all three as children
  self.house.addChild(path)
  self.house.addChild(rectangle)
  self.house.addChild(circle)

def draw(self):
  self.background(52)
  self.translate(self.mouse_x, self.mouse_y)
  self.shape(self.house)
```

## Syntax

sh.addChild(who)

sh.addChild(who, idx)

## Parameters

| Input | Description |
|-------|-------------|
| sh	(PCShape) | any variable of type PCShape |
| who	(PCShape) | any variable of type PCShape |
| idx	(int) | the layer position in which to insert the new child |

## Return

None

## Related

- [PCShape::get_child()](/docs/api/shape/PCShape/PCShape_get_child_.md)