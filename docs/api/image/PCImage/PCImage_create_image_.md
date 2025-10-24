[docs](/docs/)→[api](/docs/api)→[image](/docs/api/image/)→[PCImage](/docs/api/image/PCImage/)→[PCImage_create_image()](/docs/api/image/PCImage/PCImage_create_image_.md)

# create_image()

## Description

Creates a new PCImage (the datatype for storing images). This provides a fresh buffer of pixels to play with. Set the size of the buffer with the width and height parameters. The format parameter defines how the pixels are stored. See the PCImage reference for more information.

Be sure to include all three parameters, specifying only the width and height (but no format) will produce a strange error.

Advanced users please note that `create_image()` should be used instead of the syntax new PCImage().

## Examples

```py
"""
size(400,400);
PCImage img = createImage(264, 264, RGB);
img.load_pixels();
for (int i = 0; i < img.pixels.length; i++) {
  img.pixels[i] = color(0, 90, 102); 
}
img.update_pixels();
image(img, 68, 68);
"""
```

```py
"""
size(400,400);
PCImage img = createImage(264, 264, ARGB);
img.load_pixels();
for (int i = 0; i < img.pixels.length; i++) {
  img.pixels[i] = color(0, 90, 102, i % img.width); 
}
img.update_pixels();
image(img, 68, 68);
image(img, 136, 136);
"""
```

## Syntax

createImage(w, h, format)	

## Parameters

| Input | Description |
|-------|-------------|
| w	(int)	| width in pixels |
| h	(int)	| height in pixels |
| format	(int)	| Either RGB, ARGB, ALPHA (grayscale alpha channel) |

## Return

PCImage	

## Related

- [PCImage](docs/api/image/PCImage/PCImage.md)
- [PCGraphics](docs/api/image/PCGraphics/PCGraphics.md)