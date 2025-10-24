[docs](/docs/)→[api](/docs/api)→[image](/docs/api/image/)→[image()](/docs/api/image/loading_and_displaying/image_.md)

# image()

## Description

The `image()` function draws an image to the display window. Images must be in the sketch's "data" directory to load correctly. PyCreative currently works with GIF, JPEG, and PNG images.

The `img` parameter specifies the image to display and by default the a and b parameters define the location of its upper-left corner. The image is displayed at its original size unless the c and d parameters specify a different size. The `image_mode()` function can be used to change the way these parameters draw the image.

The color of an image may be modified with the `tint()` function. This function will maintain transparency for GIF and PNG images.

## Examples

```py
def setup(self):
    self.size(400,400)
    self.img = self.load_image("Toyokawa.jpg")

def draw(self):
    self.image(self.img, 0, 0)
```

```py
def setup(self):
    self.size(400,400)
    self.img = self.load_image("ginko.jpg")

def draw(self):
    self.image(self.img, 0, 0)
    self.image(self.img, 0, 0, self.width/2, self.height/2)
```

## Syntax

image(img, a, b)	
image(img, a, b, c, d)	

## Parameters

| Input | Description |
|-------|-------------|
| img   (PCImage) | the image to display |
| a     (float) | x-coordinate of the image by default |
| b     (float) | y-coordinate of the image by default |
| c     (float) | width to display the image by default |
| d     (float) | height to display the image by default |

## Return

None

## Related

- [loadImage()](/docs/api/image/loading_and_displaying/load_image_.md)
- [PCImage()](/docs/api/image/PCImage/PCImage.md)
- [image_mode()](/docs/api/image/loading_and_displaying/image_mode.md)
- [tint()](/docs/api/image/loading_and_displaying/tint.md)
- [background()](/docs/api/color/setting/background_.md)
- [alpha()](/docs/api/color/creating_and_reading/alpha_.md)