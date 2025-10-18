[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[keyboard](/docs/api/input/keyboard/)→[key_typed()](/docs/api/input/keyboard/key_typed_.md)

# keyCode

## Description

The variable `key_code` is used to detect special keys such as the `UP`, `DOWN`, `LEFT`, `RIGHT` arrow keys and `ALT`, `CONTROL`, `SHIFT`.

When checking for these keys, it can be useful to first check if the key is coded. This is done with the conditional `if (key == CODED)`.

The keys included in the ASCII specification (`BACKSPACE`, `TAB`, `ENTER`, `RETURN`, `ESC`, and `DELETE`) do not require checking to see if the key is coded; for those keys, you should simply use the key variable directly (and not `key_code`). If you're making cross-platform projects, note that the `ENTER` key is commonly used on PCs and Unix, while the `RETURN` key is used on Macs. Make sure your program will work on all platforms by checking for both `ENTER` and `RETURN`.

## Examples

```py
def draw(self):
    self.fill(self.fill_val)
    self.rect(25, 25, 50, 50)

def key_pressed(self):
    if self.key == 'CODED':
        if self.key_code == 'UP':
            self.fill_val = 255
        elif self.key_code == 'DOWN':
            self.fill_val = 0
    else:
        self.fill_val = 126
```

## Related

- [key](/docs/api/input/keyboard/key.md)
- [key_pressed](/docs/api/input/keyboard/key_pressed.md)
- [key_pressed()](/docs/api/input/keyboard/key_pressed_.md)
- [key_released()](/docs/api/input/keyboard/key_released_.md)