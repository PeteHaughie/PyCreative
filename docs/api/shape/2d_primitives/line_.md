[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[2d primitives](/docs/api/shape/2d_primitives/)

# line()

## Description

Draws a line (a direct path between two points) to the screen. The version of `line()` with four parameters draws the line in 2D. To color a line, use the `stroke()` function. A line cannot be filled, therefore the `fill()` function will not affect the color of a line. 2D lines are drawn with a width of one pixel by default, but this can be changed with the `stroke_weight()` function. The version with six parameters allows the line to be placed anywhere within XYZ space.

## Examples

```py
self.size(400, 400)
self.line(120, 80, 340, 300)
```

```py
self.size(400, 400)
self.line(120, 80, 340, 80)
self.stroke(126)
self.line(340, 80, 340, 300)
self.stroke(255)
self.line(340, 300, 120, 300)
```

```py
self.size(400, 400)
self.line(120, 80, 0, 340, 80, 60)
self.stroke(126)
self.line(340, 80, 60, 340, 300, 0)
self.stroke(255)
self.line(340, 300, 0, 120, 300, -200)
```

## Syntax

line(x1, y1, x2, y2)
line(x1, y1, z1, x2, y2, z2)

## Parameters

| Input | Description |
|-------|-------------|
| x1 | (float)	x-coordinate of the first point |
| y1 | (float)	y-coordinate of the first point |
| x2 | (float)	x-coordinate of the second point |
| y2 | (float)	y-coordinate of the second point |
| z1 | (float)	z-coordinate of the first point |
| z2 | (float)	z-coordinate of the second point |

## Return

None