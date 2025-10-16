[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# begin_shape()

## Class

PCShape

## Description

This method is used to start a custom shape created with the `create_shape()` function. It's always and only used with `create_shape()`.

## Examples

```py
def setup(self):
  size(100, 100)
  self.s = self.create_shape()
  self.s.begin_shape()
  self.s.fill(0, 0, 255)
  self.s.no_stroke()
  self.s.vertex(0, 0)
  self.s.vertex(0, 50)
  self.s.vertex(50, 0)
  self.s.end_shape()

def draw(self):
  self.shape(s, 25, 25)
```

## Syntax

sh.begin_shape()

sh.begin_shape(kind)	

## Parameters

| Input | Description |
|-------|-------------|
| sh	(PCShape) | any variable of type PCShape |

## Return

None

## Related

- [PCShape::end_shape()](/docs/api/shape/PCShape/PCShape_end_shape_.md)