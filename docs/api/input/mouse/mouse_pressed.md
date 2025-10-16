[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[mouse](/docs/api/input/mouse/)→[mouse_pressed](/docs/api/input/mouse/mouse_pressed.md)

# mouse_pressed

## Description

The `mouse_pressed` variable stores whether a mouse button has been pressed. The `mouse_button` variable (see the related reference entry) can be used to determine which button has been pressed.

Mouse and keyboard events only work when a program has `draw()`. Without `draw()`, the code is only run once and then stops listening for events.

## Example

```py
def draw(self):
    if self.mouse_pressed == True:
        self.fill(0)
    else:
        self.fill(255)
    self.rect(25, 25, 50, 50)
```

## Syntax

.mouse_pressed

## Return

boolean

## Related

- [mouse_x](/docs/api/input/mouse/mouse_x.md)
- [mouse_y](/docs/api/input/mouse/mouse_y.md)
- [pmouse_x](/docs/api/input/mouse/pmouse_x.md)
- [pmouse_y](/docs/api/input/mouse/pmouse_y.md)
- [mouse_pressed()](/docs/api/input/mouse/mouse_pressed_.md)
- [mouse_released()](/docs/api/input/mouse/mouse_released_.md)
- [mouse_clicked()](/docs/api/input/mouse/mouse_clicked_.md)
- [mouse_moved()](/docs/api/input/mouse/mouse_moved_.md)
- [mouse_dragged()](/docs/api/input/mouse/mouse_dragged_.md)
- [mouse_button](/docs/api/input/mouse/mouse_button.md)
- [mouse_wheel()](/docs/api/input/mouse/mouse_wheel_.md)