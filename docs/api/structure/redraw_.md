[docs](/docs/)→[api](/docs/api)→[structure](/docs/api/structure/)

# redraw()

## Description

Executes the code within `draw()` one time. This functions allows the program to update the display window only when necessary, for example when an event registered by `mouse_pressed()` or `key_pressed()` occurs.

In structuring a program, it only makes sense to call `redraw()` within events such as `mouse_pressed()`. This is because `redraw()` does not run `draw()` immediately (it only sets a flag that indicates an update is needed).

The `redraw()` function does not work properly when called inside `draw()`. To enable/disable animations, use `loop()` and `noLoop()`.

## Examples

```py
def setup(self):
  self.size(200, 200)
  self.x = 0
  self.no_loop()

def draw(self):
  self.background(204)
  self.line(self.x, 0, self.x, self.height)

def mousePressed(self):
  self.x += 1
  self.redraw()
```

## Syntax

redraw()

## Return

None

## Related
- [draw()](/docs/api/structure/draw_.md)
- [loop()](/docs/api/structure/loop_.md)
- [no_loop()](/docs/api/structure/no_loop_.md)
- [frame_rate()](/docs/api/environment/frame_rate_.md)