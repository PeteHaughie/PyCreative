[docs](/docs/)→[api](/docs/api)→[input](/docs/api/input/)→[keyboard](/docs/api/input/keyboard/)→[key_pressed()](/docs/api/input/keyboard/key_pressed_.md)

# key_pressed()

## Description

The `key_pressed()` function is called once every time a key is pressed. The key that was pressed is stored in the key variable.

For non-ASCII keys, use the `key_code` variable. The keys included in the ASCII specification (`BACKSPACE`, `TAB`, `ENTER`, `RETURN`, `ESC`, and `DELETE`) do not require checking to see if the key is coded; for those keys, you should simply use the key variable directly (and not key_code). If you're making cross-platform projects, note that the `ENTER` key is commonly used on PCs and Unix, while the `RETURN` key is used on Macs. Make sure your program will work on all platforms by checking for both `ENTER` and `RETURN`.

Because of how operating systems handle key repeats, holding down a key may cause multiple calls to `key_pressed()`. The rate of repeat is set by the operating system, and may be configured differently on each computer.

Note that there is a similarly named boolean variable called `key_pressed`. See its reference page for more information.

Mouse and keyboard events only work when a program has `draw()`. Without `draw()`, the code is only run once and then stops listening for events.

With the release of macOS Sierra, Apple changed how key repeat works, so `key_pressed` may not function as expected. See here for details of the problem and how to fix it.

## Examples

```py
def draw(self):
    self.fill(self.value)
    self.rect(25, 25, 50, 50)

def key_pressed(self):
    if self.value == 0:
        self.value = 255
    else:
        self.value = 0
```

## Syntax

key_pressed()

key_pressed(event)

## Return

void	

## Related

- [key](/docs/api/input/keyboard/key.md)
- [key_code](/docs/api/input/keyboard/key_code.md)
- [key_pressed](/docs/api/input/keyboard/key_pressed.md)
- [key_released](/docs/api/input/keyboard/key_released.md)