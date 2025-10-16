[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# delay()

## Description

The `delay()` function causes the program to halt for a specified time. Delay times are specified in thousandths of a second. For example, running `delay(3000)` will stop the program for three seconds and `delay(500)` will stop the program for a half-second.
The screen only updates when the end of draw() is reached, so delay() cannot be used to slow down drawing. For instance, you cannot use `delay()` to control the timing of an animation.

The `delay()` function should only be used for pausing scripts (i.e. a script that needs to pause a few seconds before attempting a download, or a sketch that needs to wait a few milliseconds before reading from the serial port).

## Example

```py
def setup(self):
  self.size(400, 400)
  print("Starting delay...")

def draw(self):
  self.delay(1000)
  print("1 second has passed")
```

## Syntax

delay(ms)

## Parameters

| Input | Description |
|-------|-------------|
| ms	(int) |	milliseconds to pause before running `draw()` again |

## Return

None

## Related

- [frame_rate()](/docs/api/environment/frame_rate_.md)
- [draw()](/docs/api/environment/draw_.md)
