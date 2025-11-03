[docs](/docs/)→[api](/docs/api)→[typography](/docs/api/typography)→[metrics](/docs/api/typography/metrics)→[text_descent()](/docs/api/typography/metrics/text_descent_.md)

# text_descent()

## Description

Returns descent of the current font at its current size. This information is useful for determining the height of the font below the baseline.

## Examples

```py
def setup(self):
    self.size(400, 400)
    base = self.height * 0.75
    scalar = 0.8  # Different for each font

    self.text_size(128)  # Set initial text size
    a = self.text_descent() * scalar  # Calc descent
    self.line(0, base + a, self.width, base + a)
    self.text("dp", 0, base)  # Draw text on baseline

    self.text_size(256)  # Increase text size
    a = self.text_descent() * scalar  # Recalc descent
    self.line(160, base + a, self.width, base + a)
    self.text("dp", 160, base)  # Draw text on baseline
```

## Syntax

text_descent()

## Return

float

## Related

- [text_ascent()](/docs/api/typography/metrics/text_ascent_.md)