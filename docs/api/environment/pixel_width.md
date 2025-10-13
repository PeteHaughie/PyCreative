[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# pixel_width

## Description

When `pixel_density(2)` is used to make use of a high resolution display (called a Retina display on OS X or high-dpi on Windows and Linux), the width and height of the sketch do not change, but the number of pixels is doubled. As a result, all operations that use pixels (like `load_pixels()`, `get()`, `set()`, etc.) happen in this doubled space. As a convenience, the variables `pixel_width` and `pixel_height` hold the actual width and height of the sketch in pixels. This is useful for any sketch that uses the `pixels[]` array, for instance, because the number of elements in the array will be `pixelWidth*pixelHeight`, not `width*height`.

## Example

```py
def setup(self):
  self.size(400, 400)  # Set the size of the window to 400x400 pixels
  print(self.pixel_width)  # Print the pixel width of the window (800 on a 2x Retina display)
```

## Syntax

pixel_width

## Related

- [pixel_height](/docs/api/environment/pixel_height.md)
- [height](/docs/api/environment/height.md)
- [width](/docs/api/environment/width.md)
- [size()](/docs/api/environment/size_.md)