[docs](/docs/)→[api](/docs/api)→[structure](/docs/api/structure/)

# setup()

## Description

The `setup()` function is called once when the program starts. It's used to define initial environment properties such as screen size and to load media such as images and fonts as the program starts. There can only be one `setup()` function for each program, and it shouldn't be called again after its initial execution.

If the sketch is a different dimension than the default, the `size()` function or `full_screen()` function must be the first line in `setup()`.

Note: Variables declared within `setup()` are not accessible within other functions, including `draw()`.

## Examples

```py
def setup(self):
  self.x = 0
  self.size(200, 200)
  self.background(0)
  self.no_stroke()
  self.fill(102)

def draw(self):
  self.rect(self.x, 10, 2, 80)
  self.x += 1
```

```py
def setup(self):
  self.full_screen()
  self.x = 0
  self.background(0)
  self.no_stroke()
  self.fill(102)

def draw(self):
  self.rect(self.x, self.height * 0.2, 1, self.height * 0.6)
  self.x += 2
```

## Syntax

setup()

## Return

pass

## Related

- [draw()](/docs/api/structure/draw_.md)
- [no_loop()](/docs/api/structure/no_loop_.md)
- [loop()](/docs/api/structure/loop_.md)
- [redraw()](/docs/api/structure/redraw_.md)