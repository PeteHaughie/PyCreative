[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# pixel_density()

## Description

This function makes it possible to render using all the pixels on high resolutions screens like Apple Retina and Windows HiDPI. This function can only be run once within a program, and must be called right after size() in a program without a `setup()` function, or within `setup()` if present.
`pixel_density()` should only be used with hardcoded numbers (in almost all cases this number will be 2) or in combination with `display_density()` as in the example below.

When the pixel density is set to more than 1, it changes the pixel operations including the way `get()`, `set()`, `blend()`, `copy()`, and `updatePixels()` all work. See the reference for `pixel_width` and `pixel_height` for more information.

To use variables as the arguments to `pixel_density()` function, place the `pixel_density()` function within the `settings()` function. There is more information about this on the `settings()` reference page.

## Example

```py
def setup(self):
  self.size(400, 400)
  self.pixel_density(2)  # Set pixel density to 2
```

```py
def setup(self):
  self.size(400, 400)
  self.pixel_density(self.display_density())  # Set pixel density to display density
```

## Syntax

pixel_density(value)

## Parameters

| Input | Description |
|-------|-------------|
| value (int) | The pixel density to set for the sketch (e.g., 1 or 2) |

## Return

None

## Related

- [display_density()](/docs/api/environment/display_density_.md)
- [pixel_width](/docs/api/environment/pixel_width_.md)
- [pixel_height](/docs/api/environment/pixel_height_.md)
- [settings()](/docs/api/environment/settings_.md)
- [setup()](/docs/api/environment/setup_.md)
- [draw()](/docs/api/environment/draw_.md)
