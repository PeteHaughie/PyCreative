[docs](/docs/)→[api](/docs/api)→[image](/docs/api/image/)→[PCImage](/docs/api/image/PCImage/)→[PCImage()](/docs/api/image/PCImage/PCImage.md)

# PCImage

## Description

Datatype for storing images. PyCreative can display .gif, .jpg, .tga, and .png images. Images may be displayed in 2D and 3D space. Before an image is used, it must be loaded with the `load_image()` function. The PCImage class contains fields for the width and height of the image, as well as an array called `pixels[]` that contains the values for every pixel in the image. The methods described below allow easy access to the image's pixels and alpha channel and simplify the process of compositing.

Before using the `pixels[]` array, be sure to use the `load_pixels()` method on the image to make sure that the pixel data is properly loaded.

To create a new image, use the create_image() function. Do not use the syntax new `PCImage()`.

## Examples

```py
def setup(self):
    self.size(400, 400)
    self.photo = self.load_image("Toyokawa-city.jpg")

def draw(self):
    self.image(self.photo, 0, 0)
```

## Constructors

PCImage(width, height, format, factor)	
PCImage(width, height, pixels, requiresCheckAlpha, parent)	
PCImage(width, height, pixels, requiresCheckAlpha, parent, format, factor)	
PCImage(img)	

## Fields

| Field      | Description                                      |
|------------|--------------------------------------------------|
| pixels[]   | Array containing the color of every pixel in the image |
| width      | The width of the image in units of pixels       |
| height     | The height of the image in units of pixels      |

## Methods

| Method | Description |
|--------|-------------|
| load_pixels() | Loads the pixel data for the image into its pixels[] array |
| update_pixels() | Updates the image with the data in its pixels[] array |
| resize() | Resize the image to a new width and height |
| get() | Reads the color of any pixel or grabs a rectangle of pixels |
| set() | Writes a color to any pixel or writes an image into another |
| mask() | Masks part of an image with another image as an alpha channel |
| filter() | Converts the image to grayscale or black and white |
| copy() | Copies the entire image |
| blend_color() | Blends two color values together based on the blending mode given as the MODE parameter |
| blend() | Copies a pixel or rectangle of pixels using different blending modes |
| save() | Saves the image to a TIFF, TARGA, PNG, or JPEG file |

## Related

- [load_image()](/docs/api/image/load_image_.md)
- [image_mode()](/docs/api/image/image_mode_.md)
- [create_image()](/docs/api/image/create_image_.md)