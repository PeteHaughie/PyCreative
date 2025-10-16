[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[attributes](/docs/api/shape/attributes/)

# rect_mode()

## Description

Modifies the location from which rectangles are drawn by changing the way in which parameters given to rect() are interpreted.

The default mode is rectMode(CORNER), which interprets the first two parameters of rect() as the upper-left corner of the shape, while the third and fourth parameters are its width and height.

rectMode(CORNERS) interprets the first two parameters of rect() as the location of one corner, and the third and fourth parameters as the location of the opposite corner.

rectMode(CENTER) interprets the first two parameters of rect() as the shape's center point, while the third and fourth parameters are its width and height.

rectMode(RADIUS) also uses the first two parameters of rect() as the shape's center point, but uses the third and fourth parameters to specify half of the shape's width and height.

The parameter must be written in ALL CAPS because Processing is a case-sensitive language.

## Examples
```py
self.size(400, 400)
self.rect_mode("CORNER")  # Default rectMode is CORNER
self.fill(255)  # Set fill to white
self.rect(100, 100, 200, 200)  # Draw white rect using CORNER mode

self.rect_mode("CORNERS")  # Set rectMode to CORNERS
self.fill(100)  # Set fill to gray
self.rect(100, 100, 200, 200)  # Draw gray rect using CORNERS mode
```

```py
self.size(400, 400)
self.rect_mode("RADIUS")  # Set rectMode to RADIUS
self.fill(255)  # Set fill to white
self.rect(200, 200, 120, 120)  # Draw white rect using RADIUS mode

self.rect_mode("CENTER")  # Set rectMode to CENTER
self.fill(100)  # Set fill to gray
self.rect(200, 200, 120, 120)  # Draw gray rect using CENTER mode
```

## Syntax

rect_mode(mode)

## Parameters

| Input | Description |
|-------|-------------|
| mode (String) | either "CORNER", "CORNERS", "CENTER", or "RADIUS" |

## Return

None

## Related

- [rect()](/docs/api/shape/2d_primitives/rect_.md)
- [ellipse_mode()](/docs/api/shape/attributes/ellipse_mode_.md)