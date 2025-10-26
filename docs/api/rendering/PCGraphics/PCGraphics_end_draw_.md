[docs](/docs/)→[api](/docs/api)→[rendering](/docs/api/rendering)→[PCGraphics()](/docs/api/rendering/PCGraphics/PCGraphics_.md)→[PCGraphics.endDraw()](/docs/api/rendering/PCGraphics/PCGraphics_end_draw_.md)

# end_draw()

## Class

PGraphics

## Description

Finalizes the rendering of a PCGraphics object so that it can be shown on screen.

## Examples

```py
def setup(self):
    self.size(100, 100)
    self.pg = self.create_graphics(80, 80)
    self.pg.begin_draw()
    self.pg.background(102)
    self.pg.stroke(255)
    self.pg.line(20, 20, 80, 80)
    self.pg.end_draw()
    self.no_loop()

def draw(self):
    self.image(self.pg, 10, 10)
```

## Syntax

graphics.endDraw()	

## Parameters

| Input | Description |
|-------|-------------|
| graphics	(PCGraphics)	| any object of the type PGraphics |

## Return

None

## Related

- [create_graphics()](/docs/api/rendering/create_graphics_.md)
- [PCGraphics()](/docs/api/rendering/PCGraphics/PCGraphics_.md)
- [PCGraphics.beginDraw()](/docs/api/rendering/PCGraphics/PCGraphics_begin_draw_.md)