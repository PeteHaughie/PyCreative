[docs](/docs/)→[api](/docs/api)→[rendering](/docs/api/rendering)→[noClip()](/docs/api/rendering/no_clip_.md)

# noClip()

## Description

Disables the clipping previously started by the `clip()` function.

## Examples

```py
def setup(self):
    self.size(200, 200)

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

noClip()

## Return

None

## Related

- [clip()](/docs/api/rendering/clip_.md)