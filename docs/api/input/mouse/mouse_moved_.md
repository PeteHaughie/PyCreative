[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[mouse](/docs/api/input/mouse/)→[mouse_moved()](/docs/api/input/mouse/mouse_moved_.md)

# mouse_moved()

## Description

The `mouse_moved()` function is called every time the mouse moves and a mouse button is not pressed. (If a button is being pressed, `mouse_dragged()` is called instead.)

Mouse and keyboard events only work when a program has `draw()`. Without `draw()`, the code is only run once and then stops listening for events.

## Example

```py
def setup(self):
    self.value = 0
    self.fill(self.value)
    self.rect(25, 25, 50, 50)

def draw(self):
    self.fill(self.value)
    self.rect(25, 25, 50, 50)

def mouse_moved(self):
    self.value += 5
    if self.value > 255:
        self.value = 0
```

## Syntax

.mouse_moved()

## Return

None

## Related

- [mouse_x](/docs/api/input/mouse/mouse_x.md)
- [mouse_y](/docs/api/input/mouse/mouse_y.md)
- [pmouse_x](/docs/api/input/mouse/pmouse_x.md)
- [pmouse_y](/docs/api/input/mouse/pmouse_y.md)
- [mouse_pressed](/docs/api/input/mouse/mouse_pressed_.md)
- [mouse_pressed()](/docs/api/input/mouse/mouse_pressed_.md)
- [mouse_released()](/docs/api/input/mouse/mouse_released_.md)
- [mouse_clicked()](/docs/api/input/mouse/mouse_clicked_.md)
- [mouse_dragged()](/docs/api/input/mouse/mouse_dragged_.md)
- [mouse_button](/docs/api/input/mouse/mouse_button.md)
- [mouse_wheel()](/docs/api/input/mouse/mouse_wheel_.md)