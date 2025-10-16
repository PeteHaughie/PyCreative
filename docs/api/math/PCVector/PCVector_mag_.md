[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)

# mag()

## Class

PCVector

## Description

Calculates the magnitude (length) of the vector and returns the result as a float (this is simply the equation _sqrt(x*x + y*y + z*z)_.)

## Example

```py
def setup(self):
    self.size(100, 100)
    self.v = self.pcvector(20.0, 30.0, 40.0)
    m = self.v.mag()
    print(m)  # Prints "53.851646"
```

## Syntax

.mag()

## Return

float

## Related

- [mag_sqr()](/docs/api/math/PCVector/PCVector_mag_sqr_.md)