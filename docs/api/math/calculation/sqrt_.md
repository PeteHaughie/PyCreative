[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# sqrt()

## Description

Calculates the square root of a number. The square root of a number is always positive, even though there may be a valid negative root. The square root s of number a is such that s*s = a. It is the opposite of squaring.

## Examples

```py
self.size(400, 400)
self.no_stroke()
a = self.sqrt(104976)   # Sets 'a' to 324
b = self.sqrt(10000)  # Sets 'b' to 100
c = self.sqrt(256)   # Sets 'c' to 16
self.rect(0, 100, a, 40)
self.rect(0, 180, b, 40)
self.rect(0, 260, c, 40)
```

## Syntax

sqrt(n)

## Parameters

| Inputs | Description |
|--------|-------------|
| n (float) | non-negative number |

## Return

float

## Related

- [pow()](/docs/api/math/calculation/pow_/)
- [sq()](/docs/api/math/calculation/sq_/)