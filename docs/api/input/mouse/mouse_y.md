[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[mouse](/docs/api/input/mouse/)→[mouse_y](/docs/api/input/mouse/mouse_y.md)

# mouse_y

## Description

The system variable `mouse_y` always contains the current vertical coordinate of the mouse.

Note that PyCreative can only track the mouse position when the pointer is over the current window. The default value of `mouse_y` is 0, so 0 will be returned until the mouse moves in front of the sketch window. (This typically happens when a sketch is first run.) Once the mouse moves away from the window, `mouse_y` will continue to report its most recent position.

## Example

```py
def draw(self):
    self.background(204)
    self.line(20, self.mouse_y, 80, self.mouse_y)
```

## Syntax

.mouse_y

## Return

int

## Related

- [mouse_x](/docs/api/input/mouse/mouse_x.md)
- [pmouse_x](/docs/api/input/mouse/pmouse_x.md)
- [pmouse_y](/docs/api/input/mouse/pmouse_y.md)
- [mouse_pressed](/docs/api/input/mouse/mouse_pressed_.md)
- [mouse_pressed()](/docs/api/input/mouse/mouse_pressed_.md)
- [mouse_released()](/docs/api/input/mouse/mouse_released_.md)
- [mouse_clicked()](/docs/api/input/mouse/mouse_clicked_.md)
- [mouse_moved()](/docs/api/input/mouse/mouse_moved_.md)
- [mouse_dragged()](/docs/api/input/mouse/mouse_dragged_.md)
- [mouse_button](/docs/api/input/mouse/mouse_button.md)
- [mouse_wheel()](/docs/api/input/mouse/mouse_wheel_.md)