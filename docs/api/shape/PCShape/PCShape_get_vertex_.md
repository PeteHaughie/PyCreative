[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# get_vertex()

## Class

PCShape

## Description

The `get_vertex()` method returns a `PCVector` with the coordinates of the vertex point located at the position defined by the index parameter. This method works when shapes are created as shown in the example below, but won't work properly when a shape is defined explicitly - e.g. `create_shape("RECT", 20, 20, 80, 80)`.

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

sh.get_vertex(index)	

sh.get_vertex(index, vec)

## Parameters

| Input | Description |
|-------|-------------|
| sh	(PCShape) | any variable of type PCShape |
| index	(int) | the location of the vertex |
| vec	(PCVector) | PCVector to assign the data to |

## Return

PCVector

## Related

- [PCShape::set_vertex()](/docs/api/shape/PCShape/PCShape_set_vertex_.md)
- [PCShape::get_vertex_count()](/docs/api/shape/PCShape/PCShape_get_vertex_count_.md)