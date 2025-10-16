[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)

# copy()

## Class

PCVector

## Description

Copies the components of the vector and returns the result as a `PCVector`.

## Example

```py
def setup(self):
    self.size(100, 100)
    self.v1 = self.pcvector(20.0, 30.0, 40.0)
    self.v2 = self.pcvector()
    self.v2 = self.v1.copy()
    print(self.v2.x)  # Prints "20.0"
    print(self.v2.y)  # Prints "30.0"
    print(self.v2.z)  # Prints "40.0"
```

## Syntax

.copy()

## Return

PCVector