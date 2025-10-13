[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# display_density()

## Description

The system variable `display_density` contains the pixel density of the display window. This is typically 1.0 for standard displays and 2.0 for high-density (Retina) displays.

## Example

```py
def setup(self):
  self.size(400, 400)
  self.pixel_density(self.display_density)  # Set pixel density to match display
  print(self.display_density)  # Print the display density
```

## Syntax

display_density

## Return

The pixel density of the display window.

## Related

- [pixel_density()](/docs/api/environment/pixel_density_.md)
- [setup()](/docs/api/environment/setup_.md)
- [draw()](/docs/api/environment/draw_.md)