[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)

# set()

## Class

PCVector

## Description

Sets the x, y, and z component of the vector using two or three separate variables, the data from a `PCVector`, or the values from a float array.

## Example

```py
def setup(self):
    self.size(100, 100)
    self.v = self.pcvector(0.0, 0.0, 0.0)
    self.v.set(20.0, 30.0, 40.0)
    print(self.v.x)  # Prints "20.0"
    print(self.v.y)  # Prints "30.0"
    print(self.v.z)  # Prints "40.0"
```

```py
def setup(self):
    self.size(100, 100)
    self.v1 = self.pcvector(20.0, 30.0, 40.0)
    self.v2 = self.pcvector(0.0, 0.0, 0.0)
    self.v2.set(self.v1)
    print(self.v2.x)  # Prints "20.0"
    print(self.v2.y)  # Prints "30.0"
    print(self.v2.z)  # Prints "40.0"
```

```py
def setup(self):
    self.size(100, 100)
    self.v = self.pcvector(0.0, 0.0, 0.0)
    vvv = [20.0, 30.0, 40.0]
    self.v.set(vvv)
    print(self.v.x)  # Prints "20.0"
    print(self.v.y)  # Prints "30.0"
    print(self.v.z)  # Prints "40.0"
```

## Syntax

.set(v)

.set(x, y)

.set(x, y, z)

## Parameters

| Input | Description |
|-------|-------------|
| x	(float) | the x component of the vector |
| y	(float) | the y component of the vector |
| z	(float) | the z component of the vector |
| v	(PCVector) | any variable of type PCVector |
| source	(float[]) | array to copy from |

## Returns

PCVector