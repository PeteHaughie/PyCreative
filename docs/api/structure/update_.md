[docs](/docs/)→[api](/docs/api)→[structure](/docs/api/structure/)

# update()

## Description

This function is called once every frame, before `draw()`. It can be used to update the state of the program, such as moving objects or checking for collisions.

## Examples

```py
def setup(self):
  self.size(200, 200)
  self.x = 0

def update(self):
  self.x += 1

def draw(self):
  self.background(0)
  self.fill(255)
  if (self.x > self.width):
    self.x = 0
  self.rect(self.x, self.height / 2, 5, 5)

```

## Syntax

update()

## Return

pass

## Related

- [setup()](/docs/api/structure/setup_.md)
- [draw()](/docs/api/structure/draw_.md)
- [no_loop()](/docs/api/structure/no_loop_.md)
- [loop()](/docs/api/structure/loop_.md)
- [redraw()](/docs/api/structure/redraw_.md)