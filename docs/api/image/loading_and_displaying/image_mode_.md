[docs](/docs/)→[api](/docs/api)→[image](/docs/api/image/)→[image_mode()](/docs/api/image/loading_and_displaying/image_mode_.md)

# imageMode()

## Description

Modifies the location from which images are drawn by changing the way in which parameters given to image() are interpreted.

The default mode is imageMode(CORNER), which interprets the second and third parameters of image() as the upper-left corner of the image. If two additional parameters are specified, they are used to set the image's width and height.

imageMode(CORNERS) interprets the second and third parameters of image() as the location of one corner, and the fourth and fifth parameters as the opposite corner.

imageMode(CENTER) interprets the second and third parameters of image() as the image's center point. If two additional parameters are specified, they are used to set the image's width and height.

The parameter must be written in ALL CAPS because Processing is a case-sensitive language.

## Examples

```py
def setup(self):
    self.size(400,400)
    img = self.load_image("Toyokawa.jpg")
```

```py
def setup(self):
    self.size(400,400)
    self.img = self.load_image("Toyokawa.jpg")

def draw(self):
    self.image_mode(self.CORNERS)
    self.image(self.img, 40, 40, 360, 160)  # Draw image using CORNERS mode
```

```py
def setup(self):
    self.size(400,400)
    self.img = self.load_image("Toyokawa.jpg")

def draw(self):
    self.image_mode(self.CENTER)
    self.image(self.img, 200, 200, 320, 320)  # Draw image using CENTER mode
```

## Syntax

imageMode(mode)	

## Parameters

| Input | Description |
|-------|-------------|
| mode	(int) | either CORNER, CORNERS, or CENTER |

## Return

None

## Related

- [load_image()](/docs/api/image/loading_and_displaying/load_image_.md)
- [PCImage()](/docs/api/image/PCImage/PCImage.md)
- [image()](/docs/api/image/loading_and_displaying/image_.md)
- [background()](/docs/api/color/setting/background_.md)