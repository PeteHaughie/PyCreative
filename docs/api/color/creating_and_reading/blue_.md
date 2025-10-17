[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[creating_and_reading](/docs/api/color/creating_and_reading/)→[blue_.md](/docs/api/color/creating_and_reading/blue_.md)

# blue()

## Description

Extracts the blue value from a color, scaled to match current `color_mode()`. The value is always returned as a float, so be careful not to assign it to an int value.

The blue() function is easy to use and understand, but it is slower than a technique called bit masking. When working in `color_mode(RGB, 255)`, you can achieve the same results as `blue()` but with greater speed by using a bit mask to remove the other color components. For example, the following two lines of code are equivalent means of getting the blue value of the color value c:

```py
b1 = blue(c) # Simpler, but slower to calculate
b2 = c & 0xFF # Very fast to calculate 
```

## Examples

```py
self.size(400, 400)
c = self.color(175, 100, 220)  # Define color 'c'
self.fill(c)  # Use color variable 'c' as fill color
self.rect(60, 80, 140, 240)  # Draw left rectangle

blue_value = self.blue(c)  # Get blue in 'c'
self.println(blue_value)  # Prints "220.0"
self.fill(0, 0, blue_value)  # Use 'blue_value' in new fill
self.rect(200, 80, 140, 240)  # Draw
```

## Syntax

blue(c)

## Parameters

| Input | Description |
|-------|-------------|
| c (color | int) | a color value (returned by `color()` or an integer color value) |

## Range

Returned value is a float in the current color mode's scale (default RGB range 0–255).

## Notes

Component values follow the current `color_mode()` scale. Use `color_mode()` to change numeric ranges.

## Return

float

## Related

- [red()](/docs/api/color/creating_and_reading/red_.md)
- [green()](/docs/api/color/creating_and_reading/green_.md)
- [alpha()](/docs/api/color/creating_and_reading/alpha_.md)
- [hue()](/docs/api/color/creating_and_reading/hue_.md)
- [saturation()](/docs/api/color/creating_and_reading/saturation_.md)
- [brightness()](/docs/api/color/creating_and_reading/brightness_.md)
- [rightshift()](/docs/api/bitwise/rightshift_.md)