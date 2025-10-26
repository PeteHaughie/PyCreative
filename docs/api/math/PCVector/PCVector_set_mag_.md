[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_set_mag()](/docs/api/math/PCVector/PCVector_set_mag_.md)

# set_mag()

## Class

PCVector

## Description

Set the magnitude of this vector to the value used for the `len` parameter.

## Example

```py
v = self.pcvector(3.0, 4.0, 0.0)
v.set_mag(10.0)
print(v)  # Prints something like: [ 6.0, 8.0
```

## Syntax

.set_mag(len)

.set_mag(target, len)

## Parameters

| Input | Description |
|-------|-------------|
| len	(float) | the new length for this vector |
| target	(PVector) | Set to null to create a new vector |
| len	(float) | the new length for the new vector |

## Return

PCVector