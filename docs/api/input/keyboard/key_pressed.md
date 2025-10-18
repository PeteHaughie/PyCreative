[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[keyboard](/docs/api/input/keyboard/)→[key_pressed](/docs/api/input/keyboard/key_pressed.md)

# key_pressed

## Description

The boolean system variable `key_pressed` is true if any key is pressed and false if no keys are pressed.

Note that there is a similarly named function called `key_pressed()` . See its reference page for more information.

## Examples

```py
# Note: The rectangle in this example may 
# flicker as the operating system may 
# register a long key press as a repetition
# of key presses.
def draw(self):
    if self.key_pressed == True:
        self.fill(0)
    else:
        self.fill(255)
    self.rect(25, 25, 50, 50)
```

## Related

- [key](/docs/api/input/keyboard/key.md)
- [key_code](/docs/api/input/keyboard/key_code.md)
- [key_pressed()](/docs/api/input/keyboard/key_pressed_.md)
- [key_released()](/docs/api/input/keyboard/key_released_.md)