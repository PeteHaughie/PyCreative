[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[2d primitives](/docs/api/shape/2d_primitives/)

# point()

## Description
Draws a point, a coordinate in space at the dimension of one pixel. The first parameter is the horizontal value for the point, the second value is the vertical value for the point, and the optional third value is the depth value.

Use `stroke()` to set the color of a `point()`.

Point appears round with the default `stroke_cap("ROUND")` and square with `stroke_cap("PROJECT")`. Points are invisible with `stroke_cap("SQUARE")` (no cap).

Using `point()` with `stroke_weight(1)` or smaller may draw nothing to the screen, depending on the graphics settings of the computer. Workarounds include setting the pixel using set() or drawing the point using either `circle()` or `square()`.

## Examples

```py
self.size(400, 400)
self.no_smooth()
self.point(120, 80)
self.point(340, 80)
self.point(340, 300)
self.point(120, 300)
```

```py
self.size(400, 400)
self.no_smooth()
self.point(120, 80, -200)
self.point(340, 80, -200)
self.point(340, 300, -200)
self.point(120, 300, -200)
```

## Syntax

point(x, y)	

point(x, y, z)

## Parameters

| Inputs | Description |
|--------|-------------|
| x	(float) | x-coordinate of the point |
| y	(float) | y-coordinate of the point |
| z (float) | z-coordinate of the point |

## Return

None