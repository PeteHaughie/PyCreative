[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# set_vertex()

## Class

PCShape

## Description

The `set_vertex()` method defines the coordinates of the vertex point located at the position defined by the index parameter. This method works when shapes are created as shown in the example above, but won't work properly when a shape is defined explicitly - e.g. `create_shape("RECT", 20, 20, 80, 80)`.

## Examples

```py
def setup(self):
  self.size(100, 100)
  self.s = self.create_shape()
  self.s.beginShape()
  self.s.vertex(0, 0)
  self.s.vertex(60, 0)
  self.s.vertex(60, 60)
  self.s.vertex(0, 60)
  self.s.end_shape("CLOSE")

def draw(self):
  self.translate(20, 20)
  for i in range(self.s.get_vertex_count()):
    self.pcvector v = self.s.get_vertex(i)
    v.x += self.random(-1, 1)
    v.y += self.random(-1, 1)
    self.s.setVertex(i, v)
  self.shape(self.s)
```

## Syntax

sh.setVertex(index, x, y)	

sh.setVertex(index, x, y, z)	

sh.setVertex(index, vec)

## Parameters

| Input | Description |
|-------|-------------|
| sh	(PShape) | any variable of type PShape |
| index	(int) | the location of the vertex |
| x	(float) | the x value for the vertex |
| y	(float) | the y value for the vertex |
| z	(float) | the z value for the vertex |
| vec	(PVector) | the PVector to define the x, y, z coordinates |

## Return

None

## Related

[PCShape::get_vertex()](/docs/api/shape/PCShape/PCShape_get_vertex_.md)

[PCShape::get_vertex_count()](/docs/api/shape/PCShape/PCShape_get_vertex_count_.md)