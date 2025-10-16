[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)

# mag_sq()

## Class

PCVector

## Description

Calculates the magnitude (length) of the vector, squared. This method is often used to improve performance since, unlike `mag()`, it does not require a `sqrt()` operation.

## Example

```py
def setup(self):
    self.size(100, 100)
    self.v = self.pcvector(20.0, 30.0, 40.0)
    m = self.v.mag_sq()
    print(m)  # Prints "2900.0"
```

## Syntax

.mag_sq()

## Return

float

## Related

- [mag()](/docs/api/math/PCVector/PCVector_mag_.md)