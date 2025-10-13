[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# delay()

## Description

The system variable `frame_rate` contains the approximate frame rate of the software as it executes. By default, the frame rate is set to 60 frames per second. You can change the frame rate by calling `frame_rate(fps)` in `setup()`. A value of -1 means the sketch will run as fast as possible.

## Example

```py
def setup(self):
  self.size(400, 400)
  self.frame_rate(10)  # Set frame rate to 10 frames per second

def draw(self):
  print(self.frame_rate)  # Print the current frame rate
```

## Syntax

frame_rate(fps)

## Parameters

| Input | Description |
|-------|-------------|
| fps	(int) |	frames per second to set for the sketch |

## Return

pass

## Related

- [delay()](/docs/api/environment/frame_count.md)
- [draw()](/docs/api/environment/draw_.md)
