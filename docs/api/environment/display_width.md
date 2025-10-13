[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# display_width

## Description

The system variable `display_width` contains the width of the display window in pixels.

## Example

```py
def setup(self):
  self.size(400, 400)

def draw(self):
  print(self.display_width)  # Print the current display width
```

## Syntax

display_width

## Related

- [display_height](/docs/api/environment/display_height.md)
