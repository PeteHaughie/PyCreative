[docs](/docs/)→[api](/docs/api)→[rendering](/docs/api/rendering)→[clip()](/docs/api/rendering/clip_.md)

# clip()

## Description

Limits the rendering to the boundaries of a rectangle defined by the parameters. The boundaries are drawn based on the state of the `image_mode()` function, either "CORNER", "CORNERS", or "CENTER".

## Examples

```py
def setup(self):
    self.size(200, 200)
    self.image_mode("CENTER")

def draw(self):
    self.background(204)
    if self.mouse_pressed:
        self.clip(self.mouse_x, self.mouse_y, 100, 100)
    else:
        self.no_clip()
    self.line(0, 0, self.width, self.height)
    self.line(0, self.height, self.width, 0)
```

## Syntax

clip(a, b, c, d)	

## Parameters

| Input | Description |
|-------|-------------|
| a	(float) | x-coordinate of the rectangle, by default |
| b	(float) | y-coordinate of the rectangle, by default |
| c	(float) | width of the rectangle, by default |
| d	(float) | height of the rectangle, by default |

## Return

None

## Related

- [noClip()](/docs/api/rendering/no_clip_.md)