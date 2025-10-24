[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# cursor()

## Description

Sets the cursor to a predefined symbol or an image, or makes it visible if already hidden. If you are trying to set an image as the cursor, the recommended size is 16x16 or 32x32 pixels. The values for parameters x and y must be less than the dimensions of the image.

Setting or hiding the cursor does not generally work with "Present" mode (when running full-screen).

## Example

```py
# Move the mouse left and right across the image
# to see the cursor change from a cross to a hand

def setup(self):
  self.size(100, 100)

def draw(self):
  if self.mouse_x < 50:
    self.cursor("CROSS")
  else:
    self.cursor("HAND")
```

## Syntax

cursor(kind)

cursor(img)

cursor(img, x, y)

cursor()

## Parameters

| Input | Description |
|-------|-------------|
| kind	(int) |	either ARROW, CROSS, HAND, MOVE, TEXT, or WAIT |
| img	(PCImage) |	any variable of type PCImage |
| x	(int) |	the horizontal active spot of the cursor |
| y	(int) |	the vertical active spot of the cursor |

## Return

None

## Related

- [no_cursor()](/docs/api/environment/no_cursor_.md)