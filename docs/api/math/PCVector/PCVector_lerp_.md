[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)

# lerp()

## Class

PCVector

## Description

Calculates linear interpolation from one vector to another vector. (Just like regular `lerp()`, but for vectors.)

Note that there is one static version of this method, and two non-static versions. The static version, `lerp(v1, v2, amt)` is given the two vectors to interpolate and returns a new `PVector` object. The static version is used by referencing the `PVector` class directly. (See the middle example above.) The non-static versions, `lerp(v, amt)` and `lerp(x, y, z, amt)`, do not create a new `PVector`, but transform the values of the `PVector` on which they are called. These non-static versions perform the same operation, but the former takes another vector as input, while the latter takes three float values. (See the top and bottom examples above, respectively.)

## Example

```py
def setup(self):
    self.size(200, 200)
    self.current = self.pcvector(0.0, 0.0)
    self.target = self.pcvector(100.0, 100.0)
    self.current.lerp(self.target, 0.5)
    print(self.current)  # Prints something like: [ 50.0, 50.0, 0.0 ]
```

```py
def setup(self):
    self.size(200, 200)
    self.start = self.pcvector(0.0, 0.0)
    self.end = self.pcvector(100.0, 100.0)
    self.middle = self.pcvector.lerp(self.start, self.end, 0.5)
    print(self.middle)  # Prints something like: [ 50.0, 50.0, 0.0 ]
```

```py
def setup(self):
    self.size(200, 200)
    self.v = self.pcvector(0.0, 0.0)

def draw(self):
    self.v.lerp(self.mouseX, self.mouseY, 0.0, 0.1)
    self.ellipse(self.v.x, self.v.y, 20, 20)
```

## Syntax

.lerp(v, amt)

.lerp(v1, v2, amt)

.lerp(x, y, z, amt)

## Parameters

| Input | Description |
|-------|-------------|
| v	(PVector) | the vector to lerp to |
| amt	(float) | The amount of interpolation; some value between 0.0 (old vector) and 1.0 (new vector). 0.1 is very near the old vector; 0.5 is halfway in between. |
| v1	(PVector) | the vector to start from |
| v2	(PVector) | the vector to lerp to |
| x	(float) | the x component to lerp to |
| y	(float) | the y component to lerp to |
| z	(float) | the z component to lerp to |

## Return

PCVector

## Related

- [lerp()](/docs/api/math/calculation/lerp_.md)