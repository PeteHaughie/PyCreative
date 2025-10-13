[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# no_cursor()

## Description

Hides the cursor from view. Will not work when running the program in a web browser or when running in full screen (Present) mode.

## Example

```py
// Press the mouse to hide the cursor
def draw(self):
  if (self.mouse_pressed):
    self.no_cursor()
  else:
    self.cursor("HAND")
```

## Syntax

no_cursor()

## Parameters

None

## Return

pass

## Related

- [cursor()](/docs/api/environment/cursor_.md)