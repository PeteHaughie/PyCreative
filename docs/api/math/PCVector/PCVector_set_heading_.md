[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)

# set_heading()

## Class

PCVector

## Description

Sets the angle this vector makes with the positive X axis (only 2D vectors) This is equivalent to changing the vector's direction to the given value.

## Example

```py
def setup(self):
    self.size(100, 100)
    self.v = self.pcvector(10.0, 20.0)
    self.v.set_heading(1.57)
    print(self.v.heading())  # Prints "1.57"
```

## Syntax

.set_heading(angle)

## Parameters

| Input | Description |
|-------|-------------|
| angle	(float) | the angle in radians |

## Return

PCVector

## Related

- [heading()](/docs/api/math/PCVector/PCVector_heading_.md)