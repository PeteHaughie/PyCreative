[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[2d primitives](/docs/api/shape/2d_primitives/)

# arc()

## Description
Draws an arc to the screen. Arcs are drawn along the outer edge of an ellipse defined by the a, b, c, and d parameters. The origin of the arc's ellipse may be changed with the `ellipse_mode()` function. Use the start and stop parameters to specify the angles (in radians) at which to draw the arc. The start/stop values must be in clockwise order.

There are three ways to draw an arc; the rendering technique used is defined by the optional seventh parameter. The three options are `PIE`, `OPEN`, and `CHORD`. The default mode is the `OPEN` stroke with a `PIE` fill.

In some cases, the arc() function isn't accurate enough for smooth drawing. For example, the shape may jitter on screen when rotating slowly. If you're having an issue with how arcs are rendered, you'll need to draw the arc yourself with `begin_shape()`/`end_shape()` or a PCShape.

## Examples

```py
self.size(400,400)
self.arc(50, 55, 50, 50, 0, self.HALF_PI)
self.no_fill()
self.arc(50, 55, 60, 60, self.HALF_PI, self.PI)
self.arc(50, 55, 70, 70, self.PI, self.PI + self.QUARTER_PI)
self.arc(50, 55, 80, 80, self.PI + self.QUARTER_PI, self.TWO_PI)
```

```py
self.size(400,400)
self.arc(200, 200, 320, 320, 0, self.PI + self.QUARTER_PI, "OPEN")
```

```py
self.size(400,400)
self.arc(200, 200, 320, 320, 0, self.PI + self.QUARTER_PI, "CHORD")
```

```py
self.size(400,400)
self.arc(200, 200, 320, 320, 0, self.PI + self.QUARTER_PI, "PIE")
```

## Syntax

arc(a, b, c, d, start, stop)

arc(a, b, c, d, start, stop, mode)

## Parameters

| Inputs | Description |
|--------|-------------|
| a | (float)	x-coordinate of the arc's ellipse |
| b | (float)	y-coordinate of the arc's ellipse |
| c | (float)	width of the arc's ellipse by default |
| d | (float)	height of the arc's ellipse by default |
| start | (float)	angle to start the arc, specified in radians |
| stop | (float)	angle to stop the arc, specified in radians |

## Return

None