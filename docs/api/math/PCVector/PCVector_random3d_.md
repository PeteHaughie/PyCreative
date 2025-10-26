[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)→[PCVector_random3d()](/docs/api/math/PCVector/PCVector_random3d_.md)

# random3d()

## Class

PCVector

## Description

Returns a new 3D unit vector with a random direction.  {# If you pass in this as an argument, it will use the PApplet's random number generator. #}

## Example

```py
def setup(self):
    self.size(100, 100)
    self.v = self.pcvector.random3d()
    print(self.v)
    # May print something like:
    # [ 0.61554617, -0.51195765, 0.599168 ] or 
    # [ -0.4695841, -0.14366731, -0.8711202 ] or 
    # [ 0.6091097, -0.22805278, -0.7595902 ]
```

## Syntax

.random3d()

.random3d(parent)

.random3d(target)

.random3d(parent, target)

## Parameters

| Input | Description |
|-------|-------------|
| parent	(Sketch) | the Sketch instance to associate with the new vector |
| target	(PCVector) | a PCVector to store the result in |

## Return

PCVector

## Related

- [random2d()](/docs/api/math/PCVector/PCVector_random2d_.md)