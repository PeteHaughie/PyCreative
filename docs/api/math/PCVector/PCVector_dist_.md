[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_dist()](/docs/api/math/PCVector/PCVector_dist_.md)

# dist()

## Class

PCVector

## Description

Calculates the Euclidean distance between two points (considering a point as a vector object).

## Example

```py
v1 = self.pcvector(10, 20, 0)
v2 = self.pcvector(60, 80, 0)
d = v1.dist(v2)
print(d)  # Prints "78.10249"
```

```py
v1 = self.pcvector(10, 20, 0)
v2 = self.pcvector(60, 80, 0)
d = self.pcvector.dist(v1, v2)
print(d)  # Prints "78.10249"
```

## Syntax

.dist(v)

.dist(v1, v2)

## Parameters

| Input | Description |
|-------|-------------|
| v	(PVector) | the x, y, and z coordinates of a PVector |
| v1	(PVector) | any variable of type PVector |
| v2	(PVector) | any variable of type PVector |

## Return

float