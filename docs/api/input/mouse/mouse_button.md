[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[mouse](/docs/api/input/mouse/)→[mouse_button](/docs/api/input/mouse/mouse_button.md)

# mouse_button

## Description

When a mouse button is pressed, the value of the system variable `mouse_button` is set to either "LEFT", "RIGHT", or "CENTER", depending on which button is pressed. If no button is pressed, `mouse_button` may be reset to 0. For that reason, it's best to use `mouse_pressed` first to test if any button is being pressed, and only then test the value of `mouse_button`.

## Example

```py
"""
// Click within the image and press
// the left and right mouse buttons to 
// change the value of the rectangle
void draw() {
  if (mousePressed && (mouseButton == LEFT)) {
    fill(0);
  } else if (mousePressed && (mouseButton == RIGHT)) {
    fill(255);
  } else {
    fill(126);
  }
  rect(25, 25, 50, 50);
}
"""
def draw(self):
    if self.mouse_pressed and (self.mouse_button == "LEFT"):
        self.fill(0)
    elif self.mouse_pressed and (self.mouse_button == "RIGHT"):
        self.fill(255)
    else:
        self.fill(126)
    self.rect(25, 25, 50, 50)
```

## Syntax

.mouse_button

## Return

String ("LEFT", "RIGHT", or "CENTER")

## Related

- [mouse_x](/docs/api/input/mouse/mouse_x.md)
- [mouse_y](/docs/api/input/mouse/mouse_y.md)
- [pmouse_x](/docs/api/input/mouse/pmouse_x.md)
- [pmouse_y](/docs/api/input/mouse/pmouse_y.md)
- [mouse_pressed](/docs/api/input/mouse/mouse_pressed.md)
- [mouse_pressed()](/docs/api/input/mouse/mouse_pressed_.md)
- [mouse_released()](/docs/api/input/mouse/mouse_released_.md)
- [mouse_clicked()](/docs/api/input/mouse/mouse_clicked_.md)
- [mouse_moved()](/docs/api/input/mouse/mouse_moved_.md)
- [mouse_dragged()](/docs/api/input/mouse/mouse_dragged_.md)
- [mouse_wheel()](/docs/api/input/mouse/mouse_wheel_.md)