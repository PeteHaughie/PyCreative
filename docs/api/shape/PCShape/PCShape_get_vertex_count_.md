[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# get_vertex_count()

## Class

PCShape

## Description

The `get_vertex_count()` method returns the number of vertices that make up a PCShape. In the above example, the value 4 is returned by the `get_vertex_count()` method because 4 vertices are defined in `setup()`.

## Examples

```py
def setup(self):
  self.size(100, 100)
  self.s = self.create_shape()
  self.s.begin_shape()
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

sh.get_vertex_count()	

## Parameters

| Input | Description |
|-------|-------------|
| sh	(PCShape) | any variable of type PCShape |

## Return

int	

## Related

- [PCShape::get_vertex()](/docs/api/shape/PCShape/PCShape_get_vertex_.md)
- [PCShape::set_vertex()](/docs/api/shape/PCShape/PCShape_set_vertex_.md)