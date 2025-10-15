[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# map()

## Description

Re-maps a number from one range to another.

In the first example, the number 25 is converted from a value in the range of 0 to 100 into a value that ranges from the left edge of the window (0) to the right edge (width).

As shown in the second example, numbers outside the range are not clamped to the minimum and maximum parameters values, because out-of-range values are often intentional and useful.

## Examples

```py
self.size(200, 200)
value = 25
m = self.map(value, 0, 100, 0, self.width)
self.ellipse(m, 200, 10, 10)
```

```py
value = 110
m = self.map(value, 0, 100, -20, -10)
self.println(m)  # Prints "-9.0"
```

```py
def setup(self):
    self.size(200, 200)
    self.no_stroke()

def draw(self):
    self.background(204)
    x1 = self.map(self.mouse_x, 0, self.width, 50, 150)
    self.ellipse(x1, 75, 50, 50)  
    x2 = self.map(self.mouse_x, 0, self.width, 0, 200)
    self.ellipse(x2, 125, 50, 50)
```

## Syntax

map(value, start1, stop1, start2, stop2)

## Parameters

| Inputs | Description |
|--------|-------------|
| value (float) | the incoming value to be converted |
| start1 (float) | the lower bound of the value's current range |
| stop1 (float) | the upper bound of the value's current range |
| start2 (float) | the lower bound of the value's target range |
| stop2 (float) | the upper bound of the value's target range |

## Return

float

## Related

- [norm()](/docs/api/math/calculation/norm_/)
- [lerp()](/docs/api/math/calculation/lerp_/)