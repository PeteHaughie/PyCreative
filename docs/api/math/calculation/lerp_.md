[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# lerp()

## Description

Calculates a number between two numbers at a specific increment. The `amt` parameter is the amount to interpolate between the two values where 0.0 equal to the first point, 0.1 is very near the first point, 0.5 is half-way in between, etc. The lerp function is convenient for creating motion along a straight path and for drawing dotted lines.

## Examples

```py
a = 80
b = 320
c = self.lerp(a, b, .8)
d = self.lerp(a, b, .20)
e = self.lerp(a, b, .32)
self.begin_shape(self.POINTS)
self.vertex(a, 200)
self.vertex(b, 200)
self.vertex(c, 200)
self.vertex(d, 200)
self.vertex(e, 200)
self.end_shape()
```

```py
x1 = 60
y1 = 40
x2 = 320
y2 = 360
self.line(x1, y1, x2, y2)
for i in range(41):
    x = self.lerp(x1, x2, i / 40.0) + 40
    y = self.lerp(y1, y2, i / 40.0)
    self.point(x, y)
```

## Syntax

lerp(start, stop, amt)

## Parameters

| Inputs | Description |
|--------|-------------|
| start (float) | first value |
| stop (float) | second value |
| amt (float) | float between 0.0 and 1.0 |

## Return

float

## Related

- [curve_point()](/docs/api/math/calculation/curve_point_/)
- [bezier_point()](/docs/api/math/calculation/bezier_point_/)
- [lerp_color()](/docs/api/color/creating_and_reading/lerp_color_/)