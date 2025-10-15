[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[calculation](/docs/api/math/calculation/)

# mag()

## Description

Calculates the magnitude (or length) of a vector. A vector is a direction in space commonly used in computer graphics and linear algebra. Because it has no "start" position, the magnitude of a vector can be thought of as the distance from coordinate (0,0) to its (x,y) value. Therefore, `mag()` is a shortcut for writing `dist(0, 0, x, y)`.

## Examples

```py
self.size(400, 400)

x1 = 80
x2 = 320
y1 = 120
y2 = 280

self.line(0, 0, x1, y1)
self.println(self.mag(x1, y1))  # Prints "144.22205"
self.line(0, 0, x2, y1)
self.println(self.mag(x2, y1))  # Prints "341.76016"
self.line(0, 0, x1, y2)
self.println(self.mag(x1, y2))  # Prints "291.2044"
self.line(0, 0, x2, y2)
self.println(self.mag(x2, y2))  # Prints "425.20584"
```

## Syntax

mag(x, y)

mag(x, y, z)

## Parameters

| Inputs | Description |
|--------|-------------|
| x (float) | first value |
| y (float) | second value |
| z (float) | third value |

## Return

float

## Related

- [dist()](/docs/api/math/calculation/dist_/)