[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_from_angle()](/docs/api/math/PCVector/PCVector_from_angle_.md)

# from_angle()

## Class

PCVector

## Description

Calculates and returns a new 2D unit vector from the specified angle value (in radians).

## Example

```py
def setup(self):
    self.size(100, 100)
    self.v = self.pcvector.from_angle(0.01)
    print(self.v)  # Prints something like: [ 0.99995, 0.009999833, 0.0 ]
```

## Syntax

.from_angle(angle)

.from_angle(angle, target)

## Parameters

| Input | Description |
|-------|-------------|
| angle	(float) | the angle in radians |
| target	(PCVector) | the target vector (if null a new vector will be created) |

## Return

PCVector