[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# height

## Description

The system variable `height` contains the height of the display window in pixels. It is set when the `size()` function is called, and can be used to determine the vertical dimensions of the drawing area.

## Example

```py
def setup(self):
  self.size(400, 400)  # Set the size of the window to 400x400 pixels
  print(self.height)    # Print the height of the window (400)
```

## Syntax

height

## Related

- [setup()](/docs/api/structure/setup_.md)
- [width](/docs/api/environment/width.md)
- [size()](/docs/api/environment/size_.md)