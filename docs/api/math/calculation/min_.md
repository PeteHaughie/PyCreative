[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# min()

## Description

Determines the smallest value in a sequence of numbers, and then returns that value. `min()` accepts either two or three `float` or `int` values as parameters, or an array of any length.

## Examples

```py
d = self.min(5, 9)            # Sets 'd' to 5
e = self.min(-4, -12)         # Sets 'e' to -12
f = self.min(12.3, 230.24)    # Sets 'f
```

```py
values = [5, 1, 2, -3]  # Create a list of ints
h = self.min(values)    # Sets 'h' to -3
```

## Syntax

min(a, b)

min(a, b, c)

min(array)

## Parameters

| Inputs | Description |
|--------|-------------|
| a (float, int) | numbers to compare |
| b (float, int) | numbers to compare |
| c (float, int) | numbers to compare |
| array (list of float or int) | list of numbers to compare |

## Return

float or int

## Related

- [max()](/docs/api/math/calculation/max_/) — Returns the largest of a set of values.