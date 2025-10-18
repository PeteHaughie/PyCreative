[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[keyboard](/docs/api/input/keyboard/)→[key_typed()](/docs/api/input/keyboard/key_typed_.md)

# key_typed()

## Description

The `key_typed()` function is called once every time a key is pressed, but action keys such as `Ctrl`, `Shift`, and `Alt` are ignored.

Because of how operating systems handle key repeats, holding down a key may cause multiple calls to `key_typed()`. The rate of repeat is set by the operating system, and may be configured differently on each computer.

Mouse and keyboard events only work when a program has `draw()`. Without `draw()`, the code is only run once and then stops listening for events.

## Examples

```py
# Run this program to learn how each of these functions
# relate to the others.

def draw(self):
    pass  # Empty draw() needed to keep the program running

def key_pressed(self):
    self.print("pressed " + self.key + " " + self.key_code)

def key_typed(self):
    self.print("typed " + self.key + " " + self.key_code)

def key_released(self):
    self.print("released " + self.key + " " + self.key_code)
```

## Syntax

key_typed()
key_typed(event)

## Return

void	

## Related

- [key](/docs/api/input/keyboard/key.md)
- [key_code](/docs/api/input/keyboard/key_code.md)
- [key_pressed()](/docs/api/input/keyboard/key_pressed_.md)
- [key_released()](/docs/api/input/keyboard/key_released_.md)