[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# pow()

## Description

Facilitates exponential expressions. The `pow()` function is an efficient way of multiplying numbers by themselves (or their reciprocal) in large quantities. For example, `pow(3, 5)` is equivalent to the expression 3*3*3*3*3 and `pow(3, -5)` is equivalent to 1 / 3*3*3*3*3.

## Examples

```py
a = pow(1, 3)    # Sets 'a' to 1*1*1 = 1
b = pow(3, 5)    # Sets 'b' to 3*3*3*3*3 = 243
c = pow(3, -5)   # Sets 'c' to 1 / 3*3*3*3*3 = 1 / 243 = .0041
d = pow(-3, 5)   # Sets 'd' to -3*-3*-3*-3*-3 = -243
```

## Syntax

pow(base, exponent)

## Parameters

| Inputs | Description |
|--------|-------------|
| base (float, int) | the base number |
| exponent (float, int) | the exponent |

## Return

float or int

## Related

- [sqrt()](/docs/api/math/calculation/sqrt_/) — Calculates the square root of a number.