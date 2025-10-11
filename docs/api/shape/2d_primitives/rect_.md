[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[2d primitives](/docs/api/shape/2d_primitives/)

# rect()

## Description

Draws a rectangle to the screen. A rectangle is a four-sided shape with every angle at ninety degrees. By default, the first two parameters set the location of the upper-left corner, the third sets the width, and the fourth sets the height. The way these parameters are interpreted, however, may be changed with the rectMode() function.

To draw a rounded rectangle, add a fifth parameter, which is used as the radius value for all four corners.

To use a different radius value for each corner, include eight parameters. When using eight parameters, the latter four set the radius of the arc at each corner separately, starting with the top-left corner and moving clockwise around the rectangle.

## Examples

```py
self.size(400, 400)
self.rect(120, 80, 220, 220)
```

```py
self.size(400, 400)
self.rect(120, 80, 220, 220, 28)
```

```py
self.size(400, 400)
self.rect(120, 80, 220, 220, 12, 24, 48, 72)
```

## Syntax

rect(a, b, c, d)	
rect(a, b, c, d, r)	
rect(a, b, c, d, tl, tr, br, bl)

## Parameters

| Inputs | Description |
|--------|-------------|
| a	(float) | x-coordinate of the rectangle by default |
| b	(float) | y-coordinate of the rectangle by default |
| c	(float) | width of the rectangle by default |
| d	(float) | height of the rectangle by default |
| r	(float) | radii for all four corners |
| tl	(float) | radius for top-left corner |
| tr	(float) | radius for top-right corner |
| br	(float) | radius for bottom-right corner |
| bl	(float) | radius for bottom-left corner |

## Return

pass