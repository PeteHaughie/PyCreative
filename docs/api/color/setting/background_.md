[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[setting](/docs/api/setting/)→[background_.md](/docs/api/color/setting/background_.md)

# background()

## Description

The `background()` function sets the color used for the background of the Processing window. The default background is light gray. This function is typically used within `draw()` to clear the display window at the beginning of each frame, but it can be used inside `setup()` to set the background on the first frame of animation or if the background need only be set once.

An image can also be used as the background for a sketch, although the image's width and height must match that of the sketch window. Images used with `background()` will ignore the current `tint()` setting. To resize an image to the size of the sketch window, use `image.resize(width, height)`.

It is not possible to use the transparency alpha parameter with background colors on the main drawing surface. It can only be used along with a `PCGraphics` object and `create_graphics()`.

If the background color is not set, the default is light gray (RGB value of 200).

## Examples

```py
self.background(51)  # Set background to mid gray
```

```py
self.background(152, 190, 100)  # Set background to a color
```

```py
img = self.load_image("Hokkaido.jpg")
self.background(img)
```

## Syntax

background(rgb)
background(rgb, alpha)
background(gray)
background(gray, alpha)
background(v1, v2, v3)
background(v1, v2, v3, alpha)
background(image)

## Parameters

| Input | Description |
|-------|-------------|
| rgb	(int) | any value of the color datatype |
| alpha	(float) | opacity of the background |
| gray	(float) | specifies a value between white and black |
| v1	(float) | red or hue value (depending on the current color mode) |
| v2	(float) | green or saturation value (depending on the current color mode) |
| v3	(float) | blue or brightness value (depending on the current color mode) |
| image	(PImage) | PImage to set as background (must be same size as the sketch window) |

## Return

None

## Related

- [stroke()](/docs/api/color/setting/stroke_.md)
- [fill()](/docs/api/color/setting/fill_.md)
- [tint()](/docs/api/color/setting/tint_.md)
- [color_mode()](/docs/api/color/setting/color_mode_.md)