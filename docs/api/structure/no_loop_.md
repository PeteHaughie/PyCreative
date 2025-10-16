[docs](/docs/)→[api](/docs/api)→[structure](/docs/api/structure/)

# no_loop()

## Description

Stops PyCreative from continuously executing the code within `draw()`. If `loop()` is called, the code in `draw()` begin to run continuously again. If using `no_loop()` in `setup()`, it should be the last line inside the block.

When `no_loop()` is used, it's not possible to manipulate or access the screen inside event handling functions such as `mouse_pressed()` or `key_pressed()`. Instead, use those functions to call `redraw()` or `loop()`, which will run `draw()`, which can update the screen properly. This means that when `no_loop()` has been called, no drawing can happen, and functions like `save_frame()` or `load_pixels()` may not be used.

Note that if the sketch is resized, `redraw()` will be called to update the sketch, even after `no_loop()` has been specified. Otherwise, the sketch would enter an odd state until `loop()` was called.

## Examples

```py
def setup(self):
  self.size(200, 200)
  self.x = 0

def draw(self):
  self.background(204)
  self.x += .1
  if self.x > self.width:
    self.x = 0
  self.line(self.x, 0, self.x, self.height)

def mouse_pressed(self):
  self.no_loop()

def mouse_released(self):
  self.loop()
```

```py
def setup(self):
  self.size(200, 200)
  self.no_loop()

def draw(self):
  self.line(10, 10, 190, 190)
```

```py
def setup(self):
  self.some_mode = False
  self.no_loop()

def draw(self):
  if self.some_mode:
    # do something

def mouse_pressed(self):
  self.some_mode = True
  self.redraw()  # or self.loop()
```

## Syntax

no_loop()

## Return

None

## Related

- [loop()](/docs/api/structure/loop_.md)
- [redraw()](/docs/api/structure/redraw_.md)
- [draw()](/docs/api/structure/draw_.md)