[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[attributes](/docs/api/shape/attributes/)→[stroke_cap()](/docs/api/shape/attributes/stroke_cap_/)

# stroke_cap()

## Description

Sets the style for rendering line endings. These ends are either squared, extended, or rounded, each of which specified with the corresponding parameters: `SQUARE`, `PROJECT`, and `ROUND`. The default cap is `ROUND`.

To make `point()` appear square, use `strokeCap(PROJECT)`. Using `strokeCap(SQUARE)` (no cap) causes points to become invisible.

## Examples

```py
"""
size(400, 400);
strokeWeight(48.0);
strokeCap(ROUND);
line(80, 120, 320, 120);
strokeCap(SQUARE);
line(80, 200, 320, 200);
strokeCap(PROJECT);
line(80, 280, 320, 280);
"""
```

## Syntax

strokeCap(cap)	

## Parameters


| Inputs | Description |
|--------|-------------|
| cap	(String) | either "SQUARE", "PROJECT", or "ROUND" |

## Return

void	

## Related

- [stroke()](/docs/api/color/setting/stroke_.md)
- [stroke_weight()](/docs/api/shape/attributes/stroke_weight_.md)
- [stroke_join()](/docs/api/shape/attributes/stroke_join_.md)
- [size()](/docs/api/environment/size_.md)