[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# log()

## Description

Calculates the natural logarithm (the base-_e_ logarithm) of a number. This function expects the values greater than 0.0.

## Examples

```py
def setup():
    i = 12
    self.println(self.log(i))
    self.println(self.log10(i))

# Calculates the base-10 logarithm of a number
def log10(x):
    return log(x) / log(10)
```

## Syntax

log(n)

## Parameters

| Inputs | Description |
|--------|-------------|
| n (float) | number greater than 0.0 |

## Return

float
