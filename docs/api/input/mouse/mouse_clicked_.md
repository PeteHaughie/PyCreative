[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[mouse](/docs/api/input/mouse/)→[mouse_clicked()](/docs/api/input/mouse/mouse_clicked_.md)

# mouse_clicked()

## Description

The `mouse_clicked()` function is called after a mouse button has been pressed and then released.

Mouse and keyboard events only work when a program has `draw()`. Without `draw()`, the code is only run once and then stops listening for events.

## Example

```py
def setup(self):
    self.value = 0

def draw(self):
    self.fill(self.value)
    self.rect(25, 25, 50, 50)

def mouse_clicked(self):
    if self.value == 0:
        self.value = 255
    else:
        self.value = 0
```

## Syntax

.mouse_clicked()

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
- [mouse_moved()](/docs/api/input/mouse/mouse_moved_.md)
- [mouse_dragged()](/docs/api/input/mouse/mouse_dragged_.md)
- [mouse_button](/docs/api/input/mouse/mouse_button.md)
- [mouse_wheel()](/docs/api/input/mouse/mouse_wheel_.md)