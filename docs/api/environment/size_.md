[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# size()

## Description


Defines the dimension of the display window width and height in units of pixels. In a program that has the `setup()` function, the `size()` function should be the first line of code inside `setup()`.

The built-in variables `width` and `height` are set by the parameters passed to this function. For example, running `size(640, 480)` will assign 640 to the `width` variable and 480 to the `height` variable. If `size()` is not used, the window will be given a default size of 100 x 100 pixels.

The `size()` function can only be used once inside a sketch, and it cannot be used for resizing. Use `window_resize()` instead.

To run a sketch that fills the screen, use the `full_screen()` function, rather than using `size(display_width, display_height)`.

The maximum width and height is limited by your operating system, and is usually the width and height of your actual screen. On some machines it may simply be the number of pixels on your current screen, meaning that a screen of 800 x 600 could support `size(1600, 300)`, since that is the same number of pixels. This varies widely, so you'll have to try different rendering modes and sizes until you get what you're looking for. If you need something larger, use `create_graphics()` to create a non-visible drawing surface.

The minimum width and height is around 100 pixels in each direction. This is the smallest that is supported across Windows, macOS, and Linux. We enforce the minimum size so that sketches will run identically on different machines.

## Example

```py
def setup(self):
  self.size(400, 400)
```

## Syntax

size(w, h)

## Parameters

| Input | Description |
|-------|-------------|
| w	(int) |	width of the display window in pixels |
| h	(int) |	height of the display window in pixels |

## Return

None

## Related

- [full_screen()](/docs/api/environment/full_screen.md)
- [window_resize()](/docs/api/environment/window_resize.md)
- [width](/docs/api/environment/width.md)
- [height](/docs/api/environment/height.md)
- [display_width](/docs/api/environment/display_width.md)
- [display_height](/docs/api/environment/display_height.md)