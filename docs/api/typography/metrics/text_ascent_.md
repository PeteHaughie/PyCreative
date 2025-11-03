[docs](/docs/)→[api](/docs/api)→[typography](/docs/api/typography)→[metrics](/docs/api/typography/metrics)→[text_ascentmetrics](/docs/api/typography/metrics/text_ascent_.md)

# text_ascent()

## Description

Returns ascent of the current font at its current size. This information is useful for determining the height of the font above the baseline.

## Examples

```py
def setup(self):
    self.size(400, 400)
    base = self.height * 0.75
    scalar = 0.8  # Different for each font

    self.text_size(128)  # Set initial text size
    a = self.text_ascent() * scalar  # Calc ascent
    self.line(0, base - a, self.width, base - a)
    self.text("dp", 0, base)  # Draw text on baseline

    self.text_size(256)  # Increase text size
    a = self.text_ascent() * scalar  # Recalc ascent
    self.line(160, base - a, self.width, base - a)
    self.text("dp", 160, base)  # Draw text on baseline
```

## Syntax

text_ascent()

## Return

float	

## Related

- [text_descent()](/docs/api/typography/metrics/text_descent_.md)