[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[2d primitives](/docs/api/shape/2d_primitives/)

# polygon()

## Description

Draws a polygon with the given vertex coordinates. The first pair of parameters (x1, y1) sets the first vertex and the subsequent pairs should proceed clockwise or counter-clockwise around the defined shape.

## Examples

```py
self.size(400, 400)
self.polygon(200, 100, 300, 200, 250, 300, 150, 300)
```

## Syntax

polygon(x1, y1, x2, y2, x3, y3, ..., xn, yn)

## Parameters

| Inputs | Description |
|--------|-------------|
| x1	(float) | x-coordinate of the first corner |
| y1	(float) | y-coordinate of the first corner |
| x2	(float) | x-coordinate of the second corner |
| y2	(float) | y-coordinate of the second corner |
| x3	(float) | x-coordinate of the third corner |
| y3	(float) | y-coordinate of the third corner |
| ...	(float) | Additional x and y coordinates for more corners |
| xn	(float) | x-coordinate of the nth corner |
| yn	(float) | y-coordinate of the nth corner |

## Return

pass