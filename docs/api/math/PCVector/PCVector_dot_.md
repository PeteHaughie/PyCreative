[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_dot()](/docs/api/math/PCVector/PCVector_dot_.md)

# dot()

## Class

PCVector

## Description

Calculates the dot product of two vectors.

## Example

```py
v1 = self.pcvector(10, 20, 0)
d = v1.dot(60, 80, 0)
print(d)  # Prints "2200.0"
```

```py
v1 = self.pcvector(10, 20, 0)
v2 = self.pcvector(60, 80, 0)
d = v1.dot(v2)
print(d)  # Prints "2200.0"
```

## Syntax

.dot(v)

.dot(x, y, z)

.dot(v1, v2)

## Parameters

| Input | Description |
|-------|-------------|
| v	(PVector)	| any variable of type PVector |
| x	(float)	| x component of the vector |
| y	(float)	| y component of the vector |
| z	(float)	| z component of the vector |
| v1	(PVector)	| any variable of type PVector |
| v2	(PVector)	| any variable of type PVector |

## Return

float