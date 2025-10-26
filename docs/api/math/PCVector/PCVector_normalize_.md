[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_normalize()](/docs/api/math/PCVector/PCVector_normalize_.md)

# normalize()

## Class

PCVector

## Description

Normalize the vector to length 1 (make it a unit vector).

## Example

```py
v = self.pcvector(10, 20, 2)
v.normalize()
print(v)  # Prints "PCVector(0.4454354, 0.8908708, 0.089087084)"
```

## Syntax

.normalize()

.normalize(target)

## Parameters

| Input | Description |
|-------|-------------|
| target	(PCVector) | Set to null to create a new vector |

## Return

PCVector