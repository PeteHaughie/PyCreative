[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# display_height

## Description

The system variable `display_height` contains the height of the display window in pixels.

## Example

```py
def setup(self):
  self.size(400, 400)

def draw(self):
  print(self.display_height)  # Print the current display height
```

## Syntax

display_height

## Related

- [display_width](/docs/api/environment/display_width.md)