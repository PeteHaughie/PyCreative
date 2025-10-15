[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# constrain()

## Description

Constrains a value to not exceed a minimum and maximum value.

## Examples

```py
"""
void draw() 
{ 
  background(204);
  float mx = constrain(mouseX, 30, 70);
  rect(mx-10, 40, 20, 20);
}
"""
def draw(self):
    self.background(204)
    mx = self.constrain(self.mouse_x, 30, 70)
    self.rect(mx - 10, 40, 20, 20)
```

## Syntax

constrain(n, low, high)

## Parameters

| Inputs | Description |
|--------|-------------|
| n (float, int) | the value to constrain |
| low (float, int) | minimum limit |
| high (float, int) | maximum limit |

## Return

float or int

## Related

- [min()](/docs/api/math/calculation/min_/) — Returns the smallest of a set of values.
- [max()](/docs/api/math/calculation/max_/) — Returns the largest of a