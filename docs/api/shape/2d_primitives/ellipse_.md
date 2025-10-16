[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[2d primitives](/docs/api/shape/2d_primitives/)

# ellipse()

## Description

Draws an ellipse (oval) to the screen. An ellipse with equal width and height is a circle. By default, the first two parameters set the location, and the third and fourth parameters set the shape's width and height. The origin may be changed with the `ellipse_mode()` function.

## Examples

```
self.size(400, 400)
self.ellipse(224, 184, 220, 200)
```

## Syntax

ellipse(x, y, w, h)

## Parameters

| Input | Description |
|-------|-------------|
| x	(float) | x-coordinate of the ellipse |
| y	(float) | y-coordinate of the ellipse |
| w	(float) | width of the ellipse |
| h	(float) | height of the ellipse |

## Return

None