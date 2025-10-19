[docs](/docs/)→[api](/docs/api)→[output](/docs/api/output/)→[image](/docs/api/output/image/)→[save_frame()](/docs/api/output/image/save_frame_.md)

# saveFrame()

## Description

Saves a numbered sequence of images, one image each time the function is run. To save an image that is identical to the display window, run the function at the end of `draw()` or within mouse and key events such as `mouse_pressed()` and `key_pressed()`. Use the Movie Maker program in the Tools menu to combine these images to a movie.

If save_frame() is used without parameters, it will save files as `screen-0000.png`, `screen-0001.png`, and so on. You can specify the name of the sequence with the filename parameter, including hash marks (####), which will be replaced by the current `frame_count` value. (The number of hash marks is used to determine how many digits to include in the file names.) Append a file extension, to indicate the file format to be used: either TIFF (.tif), TARGA (.tga), JPEG (.jpg), or PNG (.png). Image files are saved to the sketch's folder, which may be opened by selecting "Show Sketch Folder" from the "Sketch" menu.

Alternatively, the files can be saved to any location on the computer by using an absolute path (something that starts with / on Unix and Linux, or a drive letter on Windows).

All images saved from the main drawing window will be opaque. To save images without a background, use `create_graphics()`.

## Examples

```py
def setup(self):
    self.size(200, 200)
    self.x = 0

def draw(self):
    self.background(204)
    if self.x < 100:
        self.line(self.x, 0, self.x, 100)
        self.x += 1
    else:
        self.no_loop()
    # Saves each frame as line-000001.png, line-000002.png, etc.
    self.save_frame("line-######.png")
```

```py
def setup(self):
    self.size(200, 200)
    self.x = 0

def draw(self):
    self.background(204)
    if self.x < 100:
        self.line(self.x, 0, self.x, 100)
        self.x += 1
```

## Syntax

saveFrame()	

saveFrame(filename)	

## Parameters

| Input | Description |
|-------|-------------|
| filename	(String) | any sequence of letters or numbers that ends with either ".tif", ".tga", ".jpg", or ".png" |

## Return

None

## Related

- [save()](/docs/api/output/file/save_.md)
- [create_graphics()](/docs/api/rendering/create_graphics_.md)
- [frame_count](/docs/api/environment/frame_count.md)