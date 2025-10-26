[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_div()](/docs/api/math/PCVector/PCVector_div_.md)

# div()

## Class

PCVector

## Description

Divides a vector by a scalar. The version of the method that uses a float acts directly on the vector upon which it is called (as in the first example above). The version that receives both a `PCVector` and a `float` as arguments is a static methods, and returns a new `PCVector` that is the result of the division operation. Both examples above produce the same visual output.

## Example

```py
def setup(self):
    self.size(200, 200)
    self.v = self.pcvector(30, 60, 0)

def draw(self):
    self.ellipse(self.v.x, self.v.y, 12, 12)
    self.v.div(6)
    self.ellipse(self.v.x, self.v.y, 24, 24)
```

```py
def setup(self):
    self.size(200, 200)
    self.v1 = self.pcvector(30, 60, 0)

def draw(self):
    self.ellipse(self.v1.x, self.v1.y, 12, 12)
    self.v2 = self.pcvector.div(self.v1, 6)
    self.ellipse(self.v2.x, self.v2.y, 24, 24)
```

## Syntax

.div(n)

.div(v, n)

.div(v, n, target)

## Parameters

| Input | Description |
|-------|-------------|
| n	(float)	| the number by which to divide the vector |
| v	(PVector)	| the vector to divide by the scalar |
| target	(PVector)	| PVector in which to store the result |

## Return

PCVector