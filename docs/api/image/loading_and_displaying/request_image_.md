[docs](/docs/)→[api](/docs/api)→[image](/docs/api/image/)→[request_image()](/docs/api/image/loading_and_displaying/request_image_.md)

# request_image()

## Description

This function loads images on a separate thread so that your sketch doesn't freeze while images load during setup(). While the image is loading, its width and height will be 0. If an error occurs while loading the image, its width and height will be set to -1. You'll know when the image has loaded properly because its width and height will be greater than 0. Asynchronous image loading (particularly when downloading from a server) can dramatically improve performance.

The extension parameter is used to determine the image type in cases where the image filename does not end with a proper extension. Specify the extension as the second parameter to requestImage().

## Examples

```py
def setup(self):
    self.size(400,400)
    self.big_image = self.request_image("something.jpg")

def draw(self):
    if self.big_image.width == 0:
        # Image is not yet loaded
        pass
    elif self.big_image.width == -1:
        # This means an error occurred during image loading
        pass
    else:
        # Image is ready to go, draw it
        self.image(self.big_image, 0, 0)
```

## Syntax

request_image(filename)	

request_image(filename, extension)	

## Parameters

| Input | Description |
|-------|-------------|
| filename	(String) |	name of the file to load, can be .gif, .jpg, .tga, or a handful of other image types depending on your platform |
| extension	(String) |	the type of image to load, for example "png", "gif", "jpg" |

Return

PCImage	

Related

PCImage	
loadImage()	