[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# window_move()

## Description

The `window_move()` function defines the position of the Processing sketch in relation to the upper-left corner of the computer screen.

## Example

```py
def window_move(x, y):
    print(f"Window moved to ({x}, {y})")
```

## Syntax

window_move(x, y)

## Parameters

| Input | Description |
|-------|-------------|
| x (int) | The x-coordinate of the new window position |
| y (int) | The y-coordinate of the new window position |

## Return

None

## Related

- [window_moved()](/docs/api/environment/window_moved_.md)
