[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# fullscreen()

## Description

Toggles full screen mode on or off. When in full screen mode, the sketch will fill the entire screen and hide the operating system's menu bar and window borders. The `size()` and `fullscreen()` functions cannot both be used in the same program.

When `fullscreen()` is used without a parameter, it draws the sketch to the screen currently selected inside the Preferences window. When it is used with a single parameter, this number defines the screen to display to program on (e.g. 1, 2, 3...).

## Example

```py
def settings(self):
  self.fullscreen()  # Set the size of the display window to full screen
```

```py
def settings(self):
  self.fullscreen(2)  # Set the size of the display window to full screen on the second monitor
```

## Syntax

fullscreen()

fullscreen(display=0)

## Parameters

| Input | Description |
|-------|-------------|
| display (int, optional) | The display number to use for full screen mode (e.g., 1, 2, 3...). If not provided, uses the default display. |

## Return

None

## Related

- [settings()](/docs/api/environment/settings_.md)
- [size()](/docs/api/environment/size_.md)
- [setup()](/docs/api/environment/setup_.md)