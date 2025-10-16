[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)

# mult()

## Class

PCVector

## Description

Multiplies a vector by a scalar. The version of the method that uses a float acts directly on the vector upon which it is called (as in the first example above). The versions that receive both a `PVector` and a float as arguments are static methods, and each returns a new `PVector` that is the result of the multiplication operation. Both examples above produce the same visual output.

## Example

```py
def setup(self):
    self.size(200, 200)
    self.v = self.pcvector(40, 20, 0)

def draw(self):
    self.background(255)
    self.circle(self.v.x, self.v.y, 12)
    self.v.mult(2)
    self.circle(self.v.x, self.v.y, 24)
```

## Syntax

.mult(n)

.mult(v, n)

.mult(v, n, target)

## Parameters

| Input | Description |
|-------|-------------|
| n (float) | the number to multiply with the vector |
| v (PCVector) | the vector to multiply by the scalar |
| target (PCVector) | PVector in which to store the result |

## Return

PCVector