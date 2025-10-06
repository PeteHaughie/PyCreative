# Mouse hooks

PyCreative exposes Processing-style mouse hooks on `Sketch`:

- `mouse_pressed()` — called on mouse button down
- `mouse_released()` — called on mouse button up
- `mouse_moved()` — called when the mouse moves with no button pressed
- `mouse_dragged()` — called when the mouse moves while a button is pressed

Convenience attributes updated by the input system:

- `mouse_x`, `mouse_y` — current mouse position (read-only)
- `pmouse_x`, `pmouse_y` — previous mouse position (may be `None`)
- `mouse_is_pressed` — boolean indicating whether a button is down
- `mouse_button` — which mouse button is pressed (if any)

Example
```
class MySketch(Sketch):
    def setup(self):
        self.value = 0

    def draw(self):
        self.fill((self.value, self.value, self.value))
        self.rect(25, 25, 50, 50)

    def mouse_dragged(self):
        self.value = (self.value + 5) % 256
```

The input dispatch is robust: exceptions in user hooks are swallowed to avoid crashing sketches. If you prefer strict behavior while developing, we can add a development mode to re-raise exceptions.
