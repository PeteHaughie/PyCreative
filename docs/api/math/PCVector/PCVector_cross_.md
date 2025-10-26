[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_cross()](/docs/api/math/PCVector/PCVector_cross_.md)

# cross()

## Class

PCVector

## Description

Calculates and returns a vector composed of the cross product between two vectors.

## Example

```py
self.v1 = self.pcvector(10, 20, 2)
self.v2 = self.pcvector(60, 80, 6)
self.v3 = self.v1.cross(self.v2)
print(self.v3)  # Prints "PCVector(-40.0, 60.0, -400.0)"
```

## Syntax

.cross(v)

.cross(v, target)

.cross(v1, v2, target)

## Parameters

| Input | Description |
|-------|-------------|
| v	(PVector) | the vector to calculate the cross product |
| v	(PVector) | any variable of type PVector |
| target	(PVector) | PVector to store the result |
| v1	(PVector) | any variable of type PVector |
| v2	(PVector) | any variable of type PVector |
| target	(PVector) | PVector to store the result |

## Return

PCVector