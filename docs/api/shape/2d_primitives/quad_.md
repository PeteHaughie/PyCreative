[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[2d primitives](/docs/api/shape/2d_primitives/)

# quad()

## Description

A quad is a quadrilateral, a four sided polygon. It is similar to a rectangle, but the angles between its edges are not constrained to ninety degrees. The first pair of parameters (x1, y1) sets the first vertex and the subsequent pairs should proceed clockwise or counter-clockwise around the defined shape.

## Examples

```py
self.size(400, 400)
self.quad(152, 124, 344, 80, 276, 252, 120, 304)
```

## Syntax

quad(x1, y1, x2, y2, x3, y3, x4, y4)

## Parameters

| Inputs | Description |
|--------|-------------|
| x1	(float) | x-coordinate of the first corner |
| y1	(float) | y-coordinate of the first corner |
| x2	(float) | x-coordinate of the second corner |
| y2	(float) | y-coordinate of the second corner |
| x3	(float) | x-coordinate of the third corner |
| y3	(float) | y-coordinate of the third corner |
| x4	(float) | x-coordinate of the fourth corner |
| y4	(float) | y-coordinate of the fourth corner |

## Return

pass