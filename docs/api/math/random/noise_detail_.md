[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[random](/docs/api/math/random/)

# noise_detail()

## Description

Adjusts the character and level of detail produced by the Perlin noise function. Similar to harmonics in physics, noise is computed over several octaves. Lower octaves contribute more to the output signal and as such define the overall intensity of the noise, whereas higher octaves create finer-grained details in the noise sequence.

By default, noise is computed over 4 octaves with each octave contributing exactly half than its predecessor, starting at 50% strength for the first octave. This falloff amount can be changed by adding a function parameter. For example, a falloff factor of 0.75 means each octave will now have 75% impact (25% less) of the previous lower octave. While any number between 0.0 and 1.0 is valid, note that values greater than 0.5 may result in `noise()` returning values greater than 1.0.

By changing these parameters, the signal created by the `noise()` function can be adapted to fit very specific needs and characteristics.

## Example

```py
def setup(self):
  self.size(400, 200)
  self.noise_val = 0.0
  self.noise_scale = 0.02

def draw(self):
  for y in range(self.height):
    for x in range(self.width // 2):
      self.noise_detail(3, 0.5)
      self.noise_val = self.noise((self.mouse_x + x) * self.noise_scale,
                                  (self.mouse_y + y) * self.noise_scale)
      self.stroke(self.noise_val * 255)
      self.point(x, y)
      self.noise_detail(8, 0.65)
      self.noise_val = self.noise((self.mouse_x + x + self.width // 2) * self.noise_scale,
                                  (self.mouse_y + y) * self.noise_scale)
      self.stroke(self.noise_val * 255)
      self.point(x + self.width // 2, y)
```

## Syntax

noise_detail(lod)

noise_detail(lod, falloff)

## Parameters

| Input | Description |
|-------|-------------|
| lod (int) | The number of octaves to be used by the noise |
| falloff (float) | The falloff factor for each octave |

## Return

None

## Related

- [noise()](/docs/api/math/random/noise_.md)
- [noise_seed()](/docs/api/math/random/noise_seed_.md)