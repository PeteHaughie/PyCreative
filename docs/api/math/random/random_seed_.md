[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[random](/docs/api/math/random/)

# random_seed()

## Description

Sets the seed value for `random()`. By default, `random()` produces different results each time the program is run. Set the `seed` parameter to a constant to return the same pseudo-random numbers each time the software is run.

## Example

```py
def setup(self):
  self.random_seed(0)
  self.stroke(0, 10)

def draw(self):
  for i in range(100):
    x = self.random(self.width)
    y = self.random(self.height)
    self.point(x, y)
```

## Syntax

random_seed(seed)

## Parameters

| Input | Description |
|-------|-------------|
| seed (int) | seed value |

## Return

None

## Related

- [random()](/docs/api/math/random/random_.md)
- [noise()](/docs/api/math/random/noise_.md)
- [noise_seed()](/docs/api/math/random/noise_seed_.md)