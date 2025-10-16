[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)

# heading()

## Class

PCVector

## Description

Calculate the vector's direction, that is, the angle this vector makes with the positive X axis (only 2D vectors)

## Example

```py
def setup(self):
    self.size(100, 100)
    self.v = self.pcvector(10.0, 20.0)
    print(self.v.heading())  # Prints "1.1071488"
```

## Syntax

.heading()

## Return

float