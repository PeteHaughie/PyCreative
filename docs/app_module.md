---

## App Module: Sketch Lifecycle & API

PyCreative's `app` module provides the main entry point for creative coding sketches. The core class is `Sketch`, which manages the application loop, lifecycle hooks, frame timing, and event dispatch. Subclass `Sketch` to create interactive projects.

### Sketch Class Overview

```
class Sketch:
    """
    Base class for PyCreative sketches.

    Handles the main application loop, lifecycle hooks, frame timing, and event dispatch.
    Subclass this to create interactive creative coding projects.

    Lifecycle Methods:
        - setup(): Called once at startup. Initialize state, set size, load assets.
        - update(dt: float): Called every frame before draw. Update state, animations.
        - draw(): Called every frame. Render graphics.
        - on_event(event): Called for input events (keyboard, mouse, etc).
        - teardown(): Called on exit for cleanup.

    Core API:
        - size(width: int, height: int, fullscreen: bool = False): Set window size.
        - run(): Start the main loop.
        - clear(color: int | Tuple[int, int, int]): Clear the screen.
        - frame_rate(fps: int): Set desired frames per second.

    Attributes:
        - width (int): Current window width.
        - height (int): Current window height.
        - t (float): Elapsed time in seconds.
        - dt (float): Delta time since last frame.
    """
```

### Lifecycle Methods

#### setup(self) -> None
Called once at startup. Override to initialize state, set window size, and load assets.

**Example:**
```python
    def setup(self):
        self.size(1024, 768)
        self.bg = (30, 30, 30)
```

#### update(self, dt: float) -> None
Called every frame before draw. Override to update animation, physics, or state.

- `dt` (float): Time elapsed since last frame (seconds).

**Example:**
```python
    def update(self, dt):
        self.x += self.vx * dt
```

#### draw(self) -> None
Called every frame to render graphics. Override to draw shapes, images, etc.

**Example:**
```python
    def draw(self):
        self.clear(self.bg)
        self.rect(100, 100, 200, 200)
```

#### on_event(self, event) -> None
Called for input events (keyboard, mouse, etc). Override to handle user input.

- `event`: PyCreative event object.

**Example:**
```python
    def on_event(self, event):
        if event.type == 'KEYDOWN' and event.key == 'SPACE':
            self.bg = (255, 255, 255)
```

#### teardown(self) -> None
Called on exit for cleanup. Override to save state or release resources.

**Example:**
```python
    def teardown(self):
        print("Exiting sketch.")
```

### Minimal Usage Example

```python
from pycreative import Sketch

class MySketch(Sketch):
    def setup(self):
        self.size(800, 600)
        self.bg = 0

    def update(self, dt):
        pass

    def draw(self):
        self.clear(self.bg)
        self.ellipse(self.width/2, self.height/2, 200, 200)

if __name__ == '__main__':
    MySketch().run()
```

### Attributes
- `width` (int): Current window width
- `height` (int): Current window height
- `t` (float): Elapsed time in seconds
- `dt` (float): Delta time since last frame

### API Reference
- `size(width: int, height: int, fullscreen: bool = False)`: Set window size
- `run()`: Start the main loop
- `clear(color: int | Tuple[int, int, int])`: Clear the screen
- `frame_rate(fps: int)`: Set desired frames per second

---

For more details, see the source code in `src/pycreative/app.py` or the example sketches in `examples/`.
