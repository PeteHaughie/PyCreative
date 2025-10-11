[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[2d primitives](/docs/api/shape/2d_primitives/)

# polyline()

## Description

Draws a series of connected line segments to the screen. The first pair of parameters (x1, y1) sets the first point and the subsequent pairs should proceed clockwise or counter-clockwise around the defined shape. To color a polyline, use the `stroke()` function. A polyline cannot be filled, therefore the `fill()` function will not affect the color of a polyline. Polylines are drawn with a width of one pixel by default, but this can be changed with the `stroke_weight()` function.

## Examples

```py
self.polyline(50, 50, 150, 50, 150, 150, 50, 150, 50, 250)
```

## Syntax

polyline(x1, y1, x2, y2, x3, y3, ..., xn, yn)

## Parameters

| Inputs | Description |
|--------|-------------|
| x1	(float) | x-coordinate of the first point |
| y1	(float) | y-coordinate of the first point |
| x2	(float) | x-coordinate of the second point |
| y2	(float) | y-coordinate of the second point |
| x3	(float) | x-coordinate of the third point |
| y3	(float) | y-coordinate of the third point |
| ...	(float) | Additional x and y coordinates for more points |
| xn	(float) | x-coordinate of the nth point |
| yn	(float) | y-coordinate of the nth point |

## Return

pass