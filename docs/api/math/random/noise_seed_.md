[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[random](/docs/api/math/random/)

# noise_seed()

## Description

Sets the seed value for `noise()`. By default, `noise()` produces different results each time the program is run. Set the value parameter to a constant to return the same pseudo-random numbers each time the software is run.

## Example

```py
def setup(self):
  self.noise_seed(0)
  self.stroke(0, 10)
  self.x_off = 0.0

def draw(self):
  self.x_off += 0.01
  n = self.noise(self.x_off) * self.width
  self.line(n, 0, n, self.height)
```

## Syntax

noise_seed(seed)

## Parameters

| Input | Description |
|-------|-------------|
| seed (int) | seed value |

## Return

None

## Related

- [noise()](/docs/api/math/random/noise_.md)
- [noise_detail()](/docs/api/math/random/noise_detail_.md)
- [random()](/docs/api/math/random/random_.md)
- [random_seed()](/docs/api/math/random/random_seed_.md)