# Input Event API (pycreative.input)

## Overview
`pycreative.input` provides a unified event abstraction for keyboard and mouse input in PyCreative sketches. All events are normalized to the `Event` dataclass and dispatched to your sketch's `on_event` method.

## Event Class
```python
@dataclass
class Event:
    """
    Unified event abstraction for PyCreative.
    """
    type: str
    key: Optional[int] = None
    pos: Optional[tuple] = None
    button: Optional[int] = None
    raw: Any = None
```

### Event Types
- `type`: 'key', 'mouse', 'motion', or raw pygame event type as string
- `key`: Key code (for keyboard events)
- `pos`: (x, y) position (for mouse events)
- `button`: Mouse button (for mouse events)
- `raw`: Original pygame event object

## Usage Example
```python
def on_event(self, event):
    if event.type == 'mouse' and event.button == 1:
        print(f"Mouse click at {event.pos}")
    elif event.type == 'key' and event.key == pygame.K_SPACE:
        print("Spacebar pressed!")
```

## Dispatching Events
Events are automatically dispatched to your sketch's `on_event` method via the main loop.

---
For more details, see `src/pycreative/input.py`.
