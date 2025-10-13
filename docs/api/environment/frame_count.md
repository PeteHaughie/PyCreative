[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# frame_count

## Description

The system variable `frame_count` contains the number of frames that have been displayed since the program started. It is incremented by one each time the `draw()` function completes. For example, after 60 frames have been displayed, the value of `frame_count` will be 60.

## Example

```py
def setup(self):
  self.size(400, 400)

def draw(self):
  print(self.frame_count)  # Print the current frame count
```

## Syntax

frame_count

## Related

- [frame_rate()](/docs/api/environment/frame_rate_.md)