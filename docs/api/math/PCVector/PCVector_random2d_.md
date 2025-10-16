[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)

# random2d()

## Class

PCVector

## Description

Returns a new 2D unit vector with a random direction. {# If you pass in this as an argument, it will use the PApplet's random number generator. #}

## Example

```py
def setup(self):
    self.size(100, 100)
    self.v = self.pcvector.random2d()
    print(self.v)
    # May print something like:
    # [ -0.75006354, -0.6613658, 0.0 ] or 
    # [ 0.13742635, 0.990512, 0.0 ] or 
    # [ -0.9456181, -0.32527903, 0.0 ]
```

## Syntax

.random2d()

.random2d(parent)

.random2d(target)

.random2d(parent, target)

## Parameters

| Input | Description |
|-------|-------------|
| parent	(Sketch) | the Sketch instance to associate with the new vector |
| target	(PCVector) | a PCVector to store the result in |

## Return

PCVector

## Related

- [random3d()](/docs/api/math/PCVector/PCVector_random3d_.md)