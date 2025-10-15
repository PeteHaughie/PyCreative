[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# norm()

## Description

Normalizes a number from another range into a value between 0 and 1. Identical to `map(value, low, high, 0, 1)`.

Numbers outside the range are not clamped to 0 and 1, because out-of-range values are often intentional and useful.

## Examples

```py
value = -10
n = self.norm(value, 0, 100)
self.println(n)  # Prints "-0.1"
```

```py
value = 20
n = self.norm(value, 0, 50)
self.println(n)  # Prints "0.4"
```

## Syntax

norm(value, low, high)

## Parameters

| Inputs | Description |
|--------|-------------|
| value (float) | the incoming value to be converted |
| low (float) | the lower bound of the value's current range |
| high (float) | the upper bound of the value's current range |

## Return

float

## Related

- [map()](/docs/api/math/calculation/map_/)
- [lerp()](/docs/api/math/calculation/lerp_/)