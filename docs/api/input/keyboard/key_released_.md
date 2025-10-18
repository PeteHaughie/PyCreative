[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[keyboard](/docs/api/input/keyboard/)→[key_released()](/docs/api/input/keyboard/key_released_.md)

# key_released()

## Description

The `key_released()` function is called once every time a key is released. The key that was released will be stored in the key variable. See key and `key_code` for more information.

Mouse and keyboard events only work when a program has `draw()`. Without `draw()`, the code is only run once and then stops listening for events.

## Examples

```py
def draw(self):
    self.fill(self.value)
    self.rect(25, 25, 50, 50)

def key_released(self):
    if self.value == 0:
        self.value = 255
    else:
        self.value = 0
```

## Syntax

key_released()

key_released(event)

## Return

void	

## Related

- [key](/docs/api/input/keyboard/key.md)
- [key_code](/docs/api/input/keyboard/key_code.md)
- [key_pressed](/docs/api/input/keyboard/key_pressed_.md)
- [key_pressed()](/docs/api/input/keyboard/key_pressed_.md)