[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_array()](/docs/api/math/PCVector/PCVector_array_.md)

# array()

## Class

PCVector

## Description

Return a representation of this vector as a float array. This is only for temporary use. If used in any other fashion, the contents should be copied by using the `copy()` method to copy into your own array.

## Example

```py
v = self.pcvector(10.0, 20.0, 30.0)
f = v.array()
print(f[0])  # Prints "10.0"
print(f[1])  # Prints "20.0"
print(f[2])  # Prints "30.0"
```

## Syntax

.array()

## Return

float[]