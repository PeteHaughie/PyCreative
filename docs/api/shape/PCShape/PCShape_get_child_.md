[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# get_child()

## Class

PCShape

## Description

Extracts a child shape from a parent shape. Specify the name of the shape with the target parameter. The shape is returned as a PCShape object, or null is returned if there is an error.

## Examples

```py
def setup(self):
 self.size(400, 400)
 self.prefecture = self.load_shape("prefecture.svg")
 self.aichi = self.prefecture.get_child("AICHI") # id="AICHI" on svg file

def draw(self):
  self.aichi.disable_style()
  self.background(255)
  self.fill(255)
  self.shape(self.prefecture, 0, 5)
  self.fill(94, 138, 248); # change the color 
  self.shape(self.aichi, -10, -10); # move the location a bit
```

## Syntax

sh.get_child(index)	
sh.get_child(target)	

## Parameters

| Input | Description |
|-------|-------------|
| sh	(PCShape) | any variable of type PCShape |
| index	(int) | the layer position of the shape to get |
| target	(String) | the name of the shape to get |

## Return

PCShape	

## Related

- [PCShape::add_child()](/docs/api/shape/PCShape/PCShape_add_child_.md)