[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[2d primitives](/docs/api/shape/2d_primitives/)

# circle()

## Description

Draws a circle to the screen. By default, the first two parameters set the location of the center, and the third sets the shape's width and height. The origin may be changed with the `ellipse_mode()` function.

## Examples

```
self.size(400, 400)
self.circle(224, 184, 220)
```

## Syntax

circle(x, y, extent)

## Parameters

| Input | Description |
|-------|-------------|
| x	(float) | x-coordinate of the ellipse |
| y	(float) | y-coordinate of the ellipse |
| extent | (float)	width and height of the ellipse by default |

## Return

None