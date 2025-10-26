[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_limit()](/docs/api/math/PCVector/PCVector_limit_.md)

# limit()

## Class

PCVector

## Description

Limit the magnitude of this vector to the value used for the `max` parameter.

## Example

```py
v = self.pcvector(10, 20, 2)
v.limit(5)
print(v)  # Prints "PCVector(2.2271771, 4.4543543, 0.4454354)"
``` 

## Syntax

.limit(max)

## Parameters

| Input | Description |
|-------|-------------|
| max	(float) | the maximum magnitude for the vector |

## Return

PCVector