[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[keyboard](/docs/api/input/keyboard/)→[key](/docs/api/input/keyboard/key.md)

# key

## Description

The system variable key always contains the value of the most recent key on the keyboard that was used (either pressed or released).

For non-ASCII keys, use the `key_code` variable. The keys included in the ASCII specification (`BACKSPACE`, `TAB`, `ENTER`, `RETURN`, `ESC`, and `DELETE`) do not require checking to see if they key is coded, and you should simply use the key variable instead of `key_code` If you're making cross-platform projects, note that the ENTER key is commonly used on PCs and Unix and the `RETURN` key is used instead on Macintosh. Check for both `ENTER` and `RETURN` to make sure your program will work for all platforms.

There are issues with how `key_code` behaves across different renderers and operating systems. Watch out for unexpected behavior as you switch renderers and operating systems.

## Examples

```py
def draw(self):
    if self.key_pressed:
        if self.key == 'b' or self.key == 'B':
            self.fill(0)
    else:
        self.fill(255)
    self.rect(25, 25, 50, 50)
```

## Related

- [key_code](/docs/api/input/keyboard/key_code.md)
- [key_pressed](/docs/api/input/keyboard/key_pressed.md)
- [key_pressed()](/docs/api/input/keyboard/key_pressed.md)
- [key_released()](/docs/api/input/keyboard/key_released.md)