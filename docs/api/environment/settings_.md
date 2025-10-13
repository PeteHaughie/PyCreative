[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# settings()

## Description

The `settings()` function is called once when the program starts and before the `setup()` function. It is used to define initial environment properties such as screen size and to load media such as images and fonts as the program starts. The `settings()` function should be used to set the size of the display window with the `size()` function. If `size()` is not used in `settings()` and is not present in `setup()`, the default size of the display window will be 100x100 pixels. The `settings()` function is optional; if it is not present, the program will begin executing with default values.

## Example

```py
def settings(self):
  self.fullscreen()  # Set the size of the display window
```

```py
def settings(self):
  w = 400
  h = 400
  self.x = 0
  self.size(w, h)  # Set the size of the display window

def setup(self):
  self.background(255, 0, 0)  # Set the background color to red
  self.no_stroke()
  self.fill(102)

def draw(self):
  self.rect(self.x, 10, 1, 180)  # Draw a rectangle
  self.x += 2  # Increment x position
```

## Syntax

settings()

## Return

pass

## Related

- [setup()](/docs/api/environment/setup_.md)
- [draw()](/docs/api/environment/draw_.md)
- [size()](/docs/api/environment/size_.md)
- [fullscreen()](/docs/api/environment/fullscreen_.md)