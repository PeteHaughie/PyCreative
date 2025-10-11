[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[PCShape](/docs/api/shape/PCShape/)

# get_child_count()

## Class

PCShape

## Description

Returns the number of children within the PCShape.

## Examples

```py
def setup(self):
  self.size(100, 100)
  states = self.load_shape("tristate.svg")
  int count = states.get_child_count()
  print(count)
```

## Syntax

sh.get_child_count()	

## Parameters

| Input | Description |
|-------|-------------|
| sh	(PCShape) | any variable of type PCShape |

## Return

int	