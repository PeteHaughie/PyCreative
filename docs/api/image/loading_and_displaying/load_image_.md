[docs](/docs/)→[api](/docs/api)→[image](/docs/api/image/)→[loadImage()](/docs/api/image/loading_and_displaying/load_image_.md)

# loadImage()

## Description

Loads an image into a variable of type `PCImage`. Four types of images ( .gif, .jpg, .tga, .png) images may be loaded. To load correctly, images must be located in the data directory of the current sketch.

In most cases, load all images in `setup()` to preload them at the start of the program. Loading images inside `draw()` will reduce the speed of a program. Images cannot be loaded outside `setup()` unless they're inside a function that's called after `setup()` has already run.

Alternatively, the file maybe be loaded from anywhere on the local computer using an absolute path (something that starts with / on Unix and Linux, or a drive letter on Windows), or the filename parameter can be a URL for a file found on a network.

The extension parameter is used to determine the image type in cases where the image filename does not end with a proper extension. Specify the extension as the second parameter to `load_image()`, as shown in the third example on this page. Note that CMYK images are not supported.

Depending on the type of error, a `PCImage` object may still be returned, but the width and height of the image will be set to -1. This happens if bad image data is returned or cannot be decoded properly. Sometimes this happens with image URLs that produce a 403 error or that redirect to a password prompt, because `load_image()` will attempt to interpret the HTML as image data.

## Examples

```py
def setup(self):
    self.size(400,400)
    img = self.load_image("shells.jpg")
    self.image(img, 0, 0)
```

```py
def setup(self):
    self.size(400,400)
    self.img = self.load_image("shells.jpg")

def draw(self):
    self.image(self.img, 0, 0)
```

```py
def setup(self):
    self.size(400,400)
    url = "https://processing.org/img/processing-web.png"
    # Load image from a web server
    self.web_img = self.load_image(url, "png")

def draw(self):
    self.background(0)
    self.image(self.web_img, 0, 0)
```

## Syntax

load_image(filename)	
load_image(filename, extension)	

## Parameters

| Input | Description |
|-------|-------------|
| filename (String) | name of file to load, can be .gif, .jpg, .tga, or a handful of other image types depending on your platform |
| extension (String) | type of image to load, for example "png", "gif", "jpg" |

## Return

PCImage	

## Related

- [PCImage()](/docs/api/image/PCImage/PCImage.md)
- [image()](/docs/api/image/loading_and_displaying/image_.md)
- [image_mode()](/docs/api/image/loading_and_displaying/image_mode.md)
- [background()](/docs/api/color/setting/background_.md)