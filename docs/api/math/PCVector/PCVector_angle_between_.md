[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_angle_between()](/docs/api/math/PCVector/PCVector_angle_between_.md)

# angle_between()

## Class

PCVector

## Description

Calculates and returns the angle (in radians) between two vectors.

## Example

```py
v1 = self.pcvector(10.0, 20.0)
v2 = self.pcvector(60.0, 80.0)
a = self.pcvector.angle_between(v1, v2)
print(self.degrees(a))  # Prints "10.304827"
```

## Syntax

.angle_between(v1, v2)

## Parameters

| Input | Description |
|-------|-------------|
| v1	(PVector) | the x, y, and z components of a PVector |
| v2	(PVector) | the x, y, and z components of a PVector |

## Return

float