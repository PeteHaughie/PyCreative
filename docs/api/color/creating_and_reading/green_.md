[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[creating_and_reading](/docs/api/color/creating_and_reading/)→[green_.md](/docs/api/color/creating_and_reading/green_.md)

# green()

## Description

Extracts the green value from a color, scaled to match current `color_mode()`. The value is always returned as a float, so be careful not to assign it to an int value.

The `green()` function is easy to use and understand, but it is slower than a technique called bit shifting. When working in `color_mode(RGB, 255)`, you can achieve the same results as `green()` but with greater speed by using the right shift operator (>>) with a bit mask. For example, the following two lines of code are equivalent means of getting the green value of the color value `c`:

```py
g1 = green(c) # Simpler, but slower to calculate
g2 = c >> 8 & 0xFF # Very fast to calculate
```

## Examples
 
```py
self.size(400, 400)
c = self.color(20, 75, 200)  # Define color 'c
self.fill(c)  # Use color variable 'c' as fill color
self.rect(60, 80, 140, 240)  # Draw left rectangle

green_value = self.green(c)  # Get green in 'c'
self.println(green_value)  # Prints "75.0"
self.fill(0, green_value, 0)  # Use 'green_value' in new fill
self.rect(200, 80, 140, 240)  # Draw right rectangle
```

## Syntax

green(c)

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
- [blue()](/docs/api/color/creating_and_reading/blue_.md)
- [alpha()](/docs/api/color/creating_and_reading/alpha_.md)
- [hue()](/docs/api/color/creating_and_reading/hue_.md)
- [saturation()](/docs/api/color/creating_and_reading/saturation_.md)
- [brightness()](/docs/api/color/creating_and_reading/brightness_.md)
- [rightshift()](/docs/api/color/creating_and_reading/rightshift_.md)
