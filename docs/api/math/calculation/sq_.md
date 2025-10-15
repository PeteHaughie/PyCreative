[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# sq()

## Description

Squares a number (multiplies a number by itself). The result is always a positive number, as multiplying two negative numbers always yields a positive result. For example, -1 * -1 = 1.

## Examples

```py
self.size(400, 400)
self.no_stroke()
a = self.sq(4)    # Sets 'a' to 16
b = self.sq(-10)  # Sets 'b' to 100
c = self.sq(18)   # Sets 'c' to 324
self.rect(0, 100, a, 40)
self.rect(0, 180, b, 40)
self.rect(0, 260, c, 40)
```

## Syntax

sq(n)

## Parameters

| Inputs | Description |
|--------|-------------|
| n (float) | number to square |

## Return

float

## Related

- [sqrt()](/docs/api/math/calculation/sqrt_/)