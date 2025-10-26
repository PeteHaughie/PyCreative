[docs](/docs/)→[api](/docs/api)→[rendering](/docs/api/rendering)→[PCGraphics()](/docs/api/rendering/PCGraphics/PCGraphics_.md)

# PGraphics

## Description

Main graphics and rendering context, as well as the base API implementation for PyCreative "core". Use this class if you need to draw into an off-screen graphics buffer. A `PCGraphics` object can be constructed with the `create_graphics()` function. The `begin_draw()` and `end_draw()` methods (see above example) are necessary to set up the buffer and to finalize it. The fields and methods for this class are extensive. For a complete list, visit the developer's reference.

To create a new graphics context, use the `create_graphics()` function.

## Examples

```py
def setup(self):
    self.size(100, 100)
    self.pg = self.create_graphics(40, 40)

def draw(self):
    self.pg.begin_draw()
    self.pg.background(100)
    self.pg.stroke(255)
    self.pg.line(20, 20, self.mouse_x, self.mouse_y)
    self.pg.end_draw()
    self.image(self.pg, 9, 30)
    self.image(self.pg, 51, 30)
```

## Constructors

PGraphics()	

## Methods

beginDraw()	Sets the default properties for a PGraphics object

endDraw()	Finalizes the rendering of a PGraphics object so that it can be shown on screen

## Related

- [create_graphics()](/docs/api/rendering/create_graphics_.md)
- [PCGraphics.beginDraw()](/docs/api/rendering/PCGraphics/PCGraphics_begin_draw_.md)
- [PCGraphics.endDraw()](/docs/api/rendering/PCGraphics/PCGraphics_end_draw_.md)