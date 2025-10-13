[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# frame_rate

## Description

The system variable `frame_rate` contains the approximate frame rate of the software as it executes.

## Example

```py
def setup(self):
  self.size(400, 400)
  self.frame_rate(10)  # Set frame rate to 10 frames per second

def draw(self):
  print(self.frame_rate)  # Print the current frame rate
```

## Syntax

frame_rate

## Related

- [frame_rate()](/docs/api/environment/frame_rate_.md)
- [frame_count](/docs/api/environment/frame_count.md)