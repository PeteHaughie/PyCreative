# Observable attribute helpers

The `Observable` mixin provides an ergonomic way for examples and sketches
to react to plain attribute assignments while keeping a Processing-like API
that is easy for beginners to read and write.

Why use it
----------

- Beginners prefer simple attribute assignment (e.g. `m.mass = 2.0`).
- `Observable` lets you react to those assignments without writing
  per-attribute property boilerplate.

Basic usage
-----------

1. Inherit from `Observable`:

```python
from pycreative.observable import Observable

class Mover(Observable):
    def __init__(self):
        self.mass = 1.0
        self.radius = self.mass * 8

    def on_mass(self, new_value):
        # automatically called when `self.mass` is assigned
        self.radius = float(new_value) * 8
```

2. Now assignment works as expected for learners:

```python
m = Mover()
m.mass = 3.0  # on_mass is called and radius updates
```

Callback forms
--------------

- `on_<attr>(new)` — method called with the new value.
- `on_<attr>(old, new)` — method called with both old and new values.
- `observe(name, callback)` — explicit callback registration (callback(new_value)).
- `unobserve(name, callback=None)` — remove an explicit callback.

Notes
-----

- Observers are called after the attribute is assigned.
- Observer exceptions are swallowed to avoid breaking example code; change
  this behavior if you prefer strict failures during development.
