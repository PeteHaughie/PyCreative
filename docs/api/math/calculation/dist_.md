[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# dist()

## Description

Calculates the distance between two points.

## Examples

```py
def draw(self):
    self.no_stroke()
    d = self.dist(self.width / 2, self.height / 2, self.mouse_x, self.mouse_y)
    max_dist = self.dist(0, 0, self.width / 2, self.height / 2)
    gray = self.map(d, 0, max_dist, 0, 255)
    self.fill(gray)
    self.rect(0, 0, self.width, self.height)
```

## Syntax

dist(x1, y1, x2, y2)

dist(x1, y1, z1, x2, y2, z2)

## Parameters

| Inputs | Description |
|--------|-------------|
| x1 (float) | x-coordinate of the first point |
| y1 (float) | y-coordinate of the first point |
| z1 (float) | z-coordinate of the first point |
| x2 (float) | x-coordinate of the second point |
| y2 (float) | y-coordinate of the second point |
| z2 (float) | z-coordinate of the second point |

## Return

float