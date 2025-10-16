[docs](/docs/)→[api](/docs/api)→[structure](/docs/api/structure/)

# loop()

## Description

By default, PyCreative loops through `draw()` continuously, executing the code within it. However, the `draw()` loop may be stopped by calling `no_loop()`. In that case, the `draw()` loop can be resumed with `loop()`.

## Examples

```py
def setup(self):
  self.size(200, 200)
  self.x = 0
  self.no_loop()  # draw() will not loop

def draw(self):
  self.background(204)
  self.x += .1
  if self.x > self.width:
    self.x = 0
  self.line(self.x, 0, self.x, self.height)

def mousePressed(self):
  self.loop()  # Holding down the mouse activates looping draw()

def mouse_released(self):
  self.no_loop()  # Releasing the mouse stops looping draw()
```

## Syntax

loop()

## Return

None

## Related

- [no_loop()](/docs/api/structure/no_loop_.md)
- [redraw()](/docs/api/structure/redraw_.md)
- [draw()](/docs/api/structure/draw_.md)