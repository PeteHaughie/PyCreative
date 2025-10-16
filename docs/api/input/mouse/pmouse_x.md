[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[mouse](/docs/api/input/mouse/)→[pmouse_x](/docs/api/input/mouse/pmouse_x.md)

# pmouse_x

## Description

The system variable `pmouse_x` always contains the horizontal position of the mouse in the frame previous to the current frame.

You may find that `pmouse_x` and `pmouse_y` have different values when referenced inside of draw() and inside of mouse events like mousePressed() and mouseMoved(). Inside draw(), `pmouse_x` and `pmouse_y` update only once per frame (once per trip through the draw() loop). But inside mouse events, they update each time the event is called. If these values weren't updated immediately during events, then the mouse position would be read only once per frame, resulting in slight delays and choppy interaction. If the mouse variables were always updated multiple times per frame, then something like line(`pmouse_x`, `pmouse_y`, `mouse_x`, `mouse_y`) inside draw() would have lots of gaps, because `pmouse_x` may have changed several times in between the calls to line().

If you want values relative to the previous frame, use `pmouse_x` and `pmouse_y` inside draw(). If you want continuous response, use `pmouse_x` and `pmouse_y` inside the mouse event functions.

## Example

```py
def draw(self):
    self.background(204)
    self.line(self.mouse_x, 20, self.pmouse_x, 80)
    print(f"{self.mouse_x} : {self.pmouse_x}")
```

## Syntax

.pmouse_x

## Return

int

## Related

- [mouse_x](/docs/api/input/mouse/mouse_x.md)
- [mouse_y](/docs/api/input/mouse/mouse_y.md)
- [pmouse_y](/docs/api/input/mouse/pmouse_y.md)
- [mouse_pressed](/docs/api/input/mouse/mouse_pressed_.md)
- [mouse_pressed()](/docs/api/input/mouse/mouse_pressed_.md)
- [mouse_released()](/docs/api/input/mouse/mouse_released_.md)
- [mouse_clicked()](/docs/api/input/mouse/mouse_clicked_.md)
- [mouse_moved()](/docs/api/input/mouse/mouse_moved_.md)
- [mouse_dragged()](/docs/api/input/mouse/mouse_dragged_.md)
- [mouse_button](/docs/api/input/mouse/mouse_button.md)
- [mouse_wheel()](/docs/api/input/mouse/mouse_wheel_.md)