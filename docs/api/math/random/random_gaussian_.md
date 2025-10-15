[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[random](/docs/api/math/random/)

# random_gaussian()

## Description

Returns a float from a random series of numbers having a mean of 0 and standard deviation of 1. Each time the `random_gaussian()` function is called, it returns a number fitting a Gaussian, or normal, distribution. There is theoretically no minimum or maximum value that `random_gaussian()` might return. Rather, there is just a very low probability that values far from the mean will be returned; and a higher probability that numbers near the mean will be returned.

## Example

```py
self.size(400, 400)
for y in range(400):
  x = self.random_gaussian() * 60
  self.line(200, y, 200 + x, y)
```

```py
def setup(self):
  self.size(400, 400)
  self.distribution = [int(self.random_gaussian() * 60) for _ in range(360)]

def draw(self):
  self.background(204)
  self.translate(self.width / 2, self.height / 2)
  for dist in self.distribution:
    self.rotate(self.TWO_PI / len(self.distribution))
    self.stroke(0)
    self.line(0, 0, self.abs(dist), 0)
```

## Syntax

random_gaussian()

## Return

float

## Related

- [random()](/docs/api/math/random/random_.md)
- [noise()](/docs/api/math/random/noise_.md)
