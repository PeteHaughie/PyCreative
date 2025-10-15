[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# max()

## Description

Determines the largest value in a sequence of numbers, and then returns that value. max() accepts either two or three float or int values as parameters, or an array of any length.

## Examples

```py
a = self.max(5, 9)            # Sets 'a' to 9
b = self.max(-4, -12)         # Sets 'b' to -4
c = self.max(12.3, 230.24)    # Sets 'c' to 230.24
```

```py
values = [9, -4, 362, 21]  # Create a list of ints
d = self.max(values)       # Sets 'd' to 362
```

## Syntax

max(a, b)

max(a, b, c)

max(array)

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

- [min()](/docs/api/math/calculation/min_/) — Returns the smallest of a set of values.