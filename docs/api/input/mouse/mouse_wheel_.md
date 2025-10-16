[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[mouse](/docs/api/input/mouse/)→[mouse_wheel()](/docs/api/input/mouse/mouse_wheel_.md)

# mouse_wheel()

## Description

The code within the `mouse_wheel()` event function is run when the mouse wheel is moved. (Some mice don't have wheels and this function is only applicable with mice that have a wheel.) The `get_count()` function used within `mouse_wheel()` returns positive values when the mouse wheel is rotated down (toward the user), and negative values for the other direction (up or away from the user). On OS X with "natural" scrolling enabled, the values are opposite.

Mouse and keyboard events only work when a program has `draw()`. Without `draw()`, the code is only run once and then stops listening for events.

## Example

```py
def setup(self):
    self.size(100, 100)

def draw(self):
    pass

def mouse_wheel(self, event):
    e = event.get_count()
    print(e)
```

## Syntax

.mouse_wheel(event)

## Parameters

| Input | Description |
|-------|-------------|
| event (mouse_event) | The mouse event |

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
- [mouse_moved()](/docs/api/input/mouse/mouse_moved_.md)
- [mouse_dragged()](/docs/api/input/mouse/mouse_dragged_.md)
- [mouse_button](/docs/api/input/mouse/mouse_button.md)