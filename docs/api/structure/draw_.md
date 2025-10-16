[docs](/docs/)→[api](/docs/api)→[structure](/docs/api/structure/)

# draw()

## Description

Called directly after `setup()`, the `draw()` function continuously executes the lines of code contained inside its block until the program is stopped or `no_loop()` is called. `draw()` is called automatically and should never be called explicitly. All PyCreative programs update the screen at the end of `draw()`, never earlier.

To stop the code inside of `draw()` from running continuously, use `no_loop()`, `redraw()` and `loop()`. If `no_loop()` is used to stop the code in `draw()` from running, then `redraw()` will cause the code inside `draw()` to run a single time, and `loop()` will cause the code inside `draw()` to resume running continuously.

The number of times `draw()` executes in each second may be controlled with the `frame_rate()` function.

It is common to call `background()` near the beginning of the `draw()` loop to clear the contents of the window, as shown in the first example above. Since pixels drawn to the window are cumulative, omitting `background()` may result in unintended results.

There can only be one `draw()` function for each sketch, and `draw()` must exist if you want the code to run continuously, or to process events such as `mouse_pressed()`. Sometimes, you might have an empty call to `draw()` in your program, as shown in the second example above.

## Examples

```py
def setup(self):  # setup() runs once
  self.size(200, 200)
  self.y_pos = 0.0
  self.frameRate(30)

def draw(self):  # draw() loops forever, until stopped
  self.background(204)
  self.y_pos = self.y_pos - 1.0
  if (self.y_pos < 0):
    self.y_pos = self.height  
  self.line(0, self.y_pos, self.width, self.y_pos)
```

```py
def setup(self):
  self.size(200, 200)

# Although empty here, draw() is needed so
# the sketch can process user input events
# (mouse presses in this case).
def draw(self):
  pass

def mouse_pressed(self):
  self.line(self.mouse_x, 10, self.mouse_x, 90)
```

## Syntax

draw()

## Return

None

## Related

- [setup()](/docs/api/structure/setup_.md)
- [no_loop()](/docs/api/structure/no_loop_.md)
- [loop()](/docs/api/structure/loop_.md)
- [redraw()](/docs/api/structure/redraw_.md)
- [frame_rate()](/docs/api/structure/frame_rate_.md)
- [background()](/docs/api/color/background_.md)