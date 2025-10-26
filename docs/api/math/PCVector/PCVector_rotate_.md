[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_rotate()](/docs/api/math/PCVector/PCVector_rotate_.md)

# rotate()

## Class

PCVector

## Description

Rotate the vector by an angle (only 2D vectors), magnitude remains the same.

## Example

```py
def setup(self):
    self.size(100, 100)
    self.v = self.pcvector(10.0, 20.0)
    print(self.v)  # Prints something like: [ 10.0, 20.0, 0.0 ]
    self.v.rotate(1.57)
    print(self.v)  # Prints something like: [ -20.0, 9.999999, 0.0 ]
```

## Syntax

.rotate(theta)

## Parameters

| Input | Description |
|-------|-------------|
| theta	(float) | the angle of rotation in radians |

## Return

PCVector
