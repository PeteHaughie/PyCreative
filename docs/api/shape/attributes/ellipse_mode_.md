[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[attributes](/docs/api/shape/attributes/)

# ellipse_mode()

## Description

Modifies the location from which ellipses are drawn by changing the way in which parameters given to `ellipse()` are interpreted.

The default mode is `ellipse_mode("CENTER")`, which interprets the first two parameters of `ellipse()` as the shape's center point, while the third and fourth parameters are its width and height.

`ellipse_mode("RADIUS")` also uses the first two parameters of `ellipse()` as the shape's center point, but uses the third and fourth parameters to specify half of the shape's width and height.

`ellipse_mode("CORNER")` interprets the first two parameters of `ellipse()` as the upper-left corner of the shape, while the third and fourth parameters are its width and height.

`ellipse_mode("CORNERS")` interprets the first two parameters of `ellipse()` as the location of one corner of the ellipse's bounding box, and the third and fourth parameters as the location of the opposite corner.


## Examples
```py
self.size(400, 400)

self.ellipse_mode("RADIUS")  # Set ellipse_mode to RADIUS
self.fill(255)  # Set fill to white
self.ellipse(200, 200, 120, 120)  # Draw white ellipse using RADIUS mode
  
self.ellipse_mode("CENTER")  # Set ellipse_mode to CENTER
self.fill(100)  # Set fill to gray
self.ellipse(200, 200, 120, 120)  # Draw gray ellipse using CENTER mode
```

```py
self.size(400, 400)

self.ellipse_mode("CORNER")  # Set ellipse_mode to CORNER
self.fill(255)  # Set fill to white
self.ellipse(100, 100, 200, 200)  # Draw white ellipse using CORNER mode

self.ellipse_mode("CORNERS")  # Set ellipse_mode to CORNERS
self.fill(100)  # Set fill to gray
self.ellipse(100, 100, 200, 200)  #  Draw gray ellipse using CORNERS mode
```

## Syntax

ellipse_mode(mode)

## Parameters

| Input | Description |
|-------|-------------|
| mode (String) | either "CENTER", "RADIUS", "CORNER", or "CORNERS" |

## Return

pass

## Related

- [ellipse()](/docs/api/shape/2d_primitives/ellipse_.md)
- [arc()](/docs/api/shape/2d_primitives/arc_.md)
- [rect_mode()](/docs/api/shape/attributes/rect_mode_.md)