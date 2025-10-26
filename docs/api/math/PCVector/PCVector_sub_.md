[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_sub()](/docs/api/math/PCVector/PCVector_sub_.md)

# sub()

## Class

PCVector

## Description

Subtracts x, y, and z components from a vector, subtracts one vector from another, or subtracts two independent vectors. The version of the method that substracts two vectors is a static method and returns a `PCVector`, the others act directly on the vector. See the examples for more context. In all cases, the second vector (v2) is subtracted from the first (v1), resulting in v1‑v2.

## Example

```py
def setup(self):
    self.size(200, 200)
    self.v = self.pcvector(65, 70, 0)

def draw(self):
    self.background(255)
    self.circle(self.v.x, self.v.y, 12)
    self.circle(40, 20, 12)
    self.v.sub(40, 20, 0)
    self.circle(self.v.x, self.v.y, 24)
```

```py
def setup(self):
    self.size(200, 200)
    self.v1 = self.pcvector(65, 70, 0)
    self.v2 = self.pcvector(40, 20, 0)

def draw(self):
    self.background(255)
    self.circle(self.v1.x, self.v1.y, 12)
    self.circle(self.v2.x, self.v2.y, 12)
    self.v1.sub(self.v2)
    self.circle(self.v1.x, self.v1.y, 24)
```

```py
def setup(self):
    self.size(200, 200)
    self.v1 = self.pcvector(65, 70, 0)
    self.v2 = self.pcvector(40, 20, 0)

def draw(self):
    self.background(255)
    self.circle(self.v1.x, self.v1.y, 12)
    self.circle(self.v2.x, self.v2.y, 12)
    v3 = self.pcvector.sub(self.v1, self.v2)
    self.circle(v3.x, v3.y, 24)
```

## Syntax

.sub(v)

.sub(x, y)

.sub(x, y, z)

.sub(v1, v2)

.sub(v1, v2, target)

## Parameters

| Input | Description |
|-------|-------------|
| v	(PVector) | any variable of type PVector |
| x	(float) | the x component of the vector |
| y	(float) | the y component of the vector |
| z	(float) | the z component of the vector |
| v1	(PVector) | the x, y, and z components of a PVector object |
| v2	(PVector) | the x, y, and z components of a PVector object |
| target	(PVector) | PVector in which to store the result |

## Return

PCVector