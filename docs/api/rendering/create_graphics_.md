[docs](/docs/)→[api](/docs/api)→[rendering](/docs/api/rendering)→[create_graphics()](/docs/api/rendering/create_graphics_.md)

# create_graphics()

## Description

Creates and returns a new `PCGraphics` object. Use this class if you need to draw into an offscreen graphics buffer. The two parameters define the width and height in pixels.

It's important to run all drawing functions between the `begin_draw()` and `end_draw()`.

The `create_graphics()` function should almost never be used inside `draw()` because of the memory and time needed to set up the graphics. One-time or occasional use during `draw()` might be acceptable, but code that calls `create_graphics()` at 60 frames per second might run out of memory or freeze your sketch.

Unlike the main drawing surface which is completely opaque, surfaces created with `create_graphics()` can have transparency. This makes it possible to draw into a graphics and maintain the alpha channel. By using `save()` to write a `PNG` or `TGA` file, the transparency of the graphics object will be honored.

## Examples

```py
def setup(self):
    self.size(200, 200)
    self.pg = self.create_graphics(100, 100)

def draw(self):
    self.pg.begin_draw()
    self.pg.background(102)
    self.pg.stroke(255)
    self.pg.line(self.pg.width * 0.5, self.pg.height * 0.5, self.mouse_x, self.mouse_y)
    self.pg.end_draw()
    self.image(self.pg, 50, 50)
```

## Syntax

create_graphics(w, h)	

## Parameters

| Input | Description |
|-------|-------------|
| w	(int) | width in pixels |
| h	(int) | height in pixels |

## Return

PCGraphics	