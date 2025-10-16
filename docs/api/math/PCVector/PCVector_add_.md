[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)

# add()

## Class

PCVector

## Description

Adds x, y, and z components to a vector, adds one vector to another, or adds two independent vectors together. The version of the method that adds two vectors together is a static method and returns a new `PCVector`, the others act directly on the vector itself. See the examples for more context.

## Example

```py
def setup(self):
    self.size(200, 200)
    self.v1 = self.pcvector(40, 20)
    self.v2 = self.pcvector(25, 50)

def draw(self):
    self.circle(self.v1.x, self.v1.y, 12)
    self.circle(self.v2.x, self.v2.y, 12)
    self.v2.add(self.v1)
    self.circle(self.v2.x, self.v2.y, 24)
```

## Example

```py
def setup(self):
    self.size(200, 200)
    self.v = self.pcvector(40, 20)

def draw(self):
    self.circle(self.v.x, self.v.y, 12)
    self.circle(25, 50, 12)
    self.v.add(25, 50)
    self.circle(self.v.x, self.v.y, 24)
```

## Example

```py
def setup(self):
    self.size(200, 200)
    self.v1 = self.pcvector(40, 20)
    self.v2 = self.pcvector(25, 50)

def draw(self):
    self.circle(self.v1.x, self.v1.y, 12)
    self.circle(self.v2.x, self.v2.y, 12)
    v3 = self.pcvector.add(self.v1, self.v2)
    self.circle(v3.x, v3.y, 24)
```

## Syntax

.add(v)

.add(x, y)

.add(x, y, z)

.add(v1, v2)

.add(v1, v2, target)

## Parameters

| Input | Description |
|-------|-------------|
| v	(PVector)	| the vector to be added |
| x	(float) | x component of the vector |
| y	(float) | y component of the vector |
| z	(float) | z component of the vector |
| v1	(PVector) | a vector |
| v2	(PVector) | another vector |
| target	(PVector) | the target vector (if null, a new vector will be created) |

## Return

PCVector