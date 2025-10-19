# Keyboard input — developer notes

This document describes the keyboard input path used by PyCreative during
interactive (pyglet) runs and headless testing. It explains the adapter
normalization, Engine wiring, event shape, and developer testing tips.

These notes are intended for contributors and maintainers who work on
input adapters or the Engine wiring.

## Overview

- Platform events are normalized by a small adapter (`core.adapters.pyglet_keyboard`) so the
  Engine sees a stable, cross-platform event shape.
- The Engine exposes serialised, Processing-like system variables on the
  engine instance and also provides a `SimpleSketchAPI` facade used by
  sketches. For class-based sketches the Engine creates a dynamic subclass
  that exposes convenience properties like `self.key`, `self.key_code`, and
  a bool/callable `self.key_pressed` proxy.
- Tests may use `Engine.simulate_key_press` / `simulate_key_release` to
  emulate key events in headless mode.

## Adapter: `core.adapters.pyglet_keyboard`

Responsibilities:

- Lazily import `pyglet` so headless tests don't require the dependency.
- Normalize a variety of input shapes:
  - Raw pyglet event objects (attributes `symbol`, `string`, `modifiers`, `repeat`).
  - Plain dicts that represent an event (useful for tests and simulation).
- Produce a canonical event dict with at least the keys: `key`, `key_code`,
  `modifiers`, and `repeat`.

Event semantics implemented:

- `key`: a printable character (single-character string) if the pressed key
  has a printable representation (letters, digits). For non-printable keys
  this will be one of:
  - `'CODED'` — a Processing-style sentinel indicating a coded key (e.g.
    arrow keys, function keys) when the adapter could not derive a printable
    character.
  - A numeric string like `'1'` when the key constant encoded a digit
    (e.g. `NUM_1`, `KP_3`) — the adapter converts trailing digits into
    printable `key` values.
- `key_code`: a canonical name for special keys (e.g. `'LEFT'`, `'F1'`). For
  digit mappings where the digit was promoted to `key`, `key_code` will be
  `None` by default (the adapter favors a printable `key` value for numeric
  keys). If you require the original key code (to distinguish keypad vs
  main-row numbers), update the adapter to preserve `key_code` as well.
- `modifiers`: list of modifier names present on the event (e.g. `['SHIFT']`).
- `repeat`: boolean indicating whether the OS generated a repeated key
  event.

Normalization details & decisions

- Trailing underscores in pyglet constant names (e.g. `return_`) are stripped
  to produce canonical names like `RETURN`.
- If the adapter receives a dict that already contains `key` or `key_code`,
  those explicit values are preserved where possible. This makes unit tests
  and `simulate_*` helpers robust.
- Digit-aware mapping: key constants ending in digits (e.g. `NUM_1`, `KP_3`)
  will be converted to the numeric string and returned as `key='1'` (with
  `key_code` cleared). This matches the common expectation that numeric
  keys produce printable characters.
- For other non-printable keys we set `key='CODED'` and `key_code` to the
  canonical name. Sketches can test `if self.key == 'CODED':` to detect
  coded keys and then inspect `self.key_code`.

## Engine wiring (where events become system variables)

- Windowed runs register pyglet event handlers on the Engine's window:
  - `on_key_press(symbol, modifiers)` and `on_key_release(symbol, modifiers)`
  - These handlers call into `core.adapters.pyglet_keyboard.normalize_event`
    to obtain the canonical event dict.
- The Engine updates the following system variables based on the adapter's
  output:
  - `engine.key` — printable character or `'CODED'` (or digits).
  - `engine.key_code` — canonical name for special keys (or `None`).
  - `engine.key_pressed` — boolean; set True on press and False on release.
- For class-based sketches the Engine exposes `self.key`, `self.key_code`,
  and `self.key_pressed` (callable/bool proxy) via a dynamic subclass so
  sketch authors can use Processing-style code directly.

## Testing & simulation

- Use `Engine.simulate_key_press(key=..., key_code=..., event=...)` and
  `Engine.simulate_key_release(...)` to emulate key input in headless tests.
- The adapter accepts dict-shaped events, which makes writing tests easy:

```py
eng.simulate_key_press(event={'key': None, 'key_code': 'LEFT'})
assert eng.key == 'CODED'
assert eng.key_code == 'LEFT'
```

- For numeric keypad or numeric key handling you can simulate either the
  printable key or provide a `key_code` like `NUM_1` and rely on the adapter
  to map it to `'1'`.

## Extensibility notes for contributors

- If you need to preserve keypad vs main-row numeric distinction (e.g.
  `KP_1` vs `1`), update the adapter to both set `key='1'` and preserve
  `key_code='KP_1'` instead of clearing `key_code`.
- Additions to the adapter should remain defensive: prefer shallow-copying
  incoming dicts and avoid failing when pyglet is unavailable.
- When adding new behaviors, update `tests/core/adapters/test_pyglet_keyboard.py`
  and `tests/core/input/test_keyboard_integration.py` to cover both printable
  and coded key cases.

## Troubleshooting

- If sketches see `self.key` as `None`:
  - Confirm the upstream pyglet event has a printable character (check
    `event.string` or `event.symbol`). If not, `key` will be `'CODED'` and
    `key_code` will contain the name of the key.
  - Use `eng.simulate_key_press(...)` with explicit `key`/`key_code` in tests
    to reproduce the case reliably.

## Example: key handler in a sketch

```py
def key_pressed(self):
    if self.key == 'CODED':
        if self.key_code == 'LEFT':
            # handle left arrow
            pass
    elif self.key == '1':
        # handle number 1
        pass
```

## Where to look in code

- Adapter: `src/core/adapters/pyglet_keyboard.py`
- Engine wiring & proxies: `src/core/engine/impl.py`
- Headless simulation helpers: `Engine.simulate_key_press` / `simulate_key_release`
- Tests: `tests/core/adapters/test_pyglet_keyboard.py`,
  `tests/core/input/test_keyboard_integration.py`

