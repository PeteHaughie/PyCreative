[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# width

## Description

The system variable `width` contains the width of the display window in pixels. It is set when the `size()` function is called, and can be used to determine the horizontal dimensions of the drawing area.

## Example

```py
def setup(self):  
  self.size(400, 400)  # Set the size of the window to 400x400 pixels
  print(self.width)     # Print the width of the window (400)
```

## Syntax

width

## Related

- [setup()](/docs/api/structure/setup_.md)
- [height](/docs/api/environment/height.md)
- [size()](/docs/api/environment/size_.md)