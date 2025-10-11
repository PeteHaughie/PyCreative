[docs](/docs/)→[api](/docs/api)→[color](/docs/api/color/)→[setting](/docs/api/setting/)

# color_mode()

## Description

Changes the way PyCreative interprets color data. By default, the parameters for `fill()`, `stroke()`, `background()`, and `color()` are defined by values between 0 and 255 using the RGB color model. The `color_mode()` function is used to change the numerical range used for specifying colors and to switch color systems. For example, calling `color_mode("RGB", 1.0)` will specify that values are specified between 0 and 1. The limits for defining colors are altered by setting the parameters max, max1, max2, max3, and maxA.

After changing the range of values for colors with code like `color_mode("HSB", 360, 100, 100)`, those ranges remain in use until they are explicitly changed again. For example, after running `color_mode("HSB", 360, 100, 100)` and then changing back to `color_mode("RGB")`, the range for R will be 0 to 360 and the range for G and B will be 0 to 100. To avoid this, be explicit about the ranges when changing the color mode. For instance, instead of `color_mode("RGB")`, write `color_mode("RGB", 255, 255, 255)`.

## Examples

```py
self.size(400, 400)
self.no_stroke()
self.color_mode("RGB", 400)
for i in range(400):
  for j in range(400):
    self.fill(i, j, 0)
    self.point(i, j)
```

```py
self.size(400, 400)
self.no_stroke()
self.color_mode("HSB", 400)
for i in range(400):
  for j in range(400):
    self.fill(i, 400, j)
    self.point(i, j)
```

```py
# If the color is defined here, it won't be 
# affected by the color_mode() in setup(). 
# Instead, just declare the variable here and 
# assign the value after the color_mode() in setup()

def setup(self):
  self.size(400, 400)
  self.color_mode("HSB", 360, 100, 100)
  self.bg = self.color(180, 50, 50)

def draw(self):
  self.background(self.bg)
```

## Syntax

color_mode(mode)

color_mode(mode, max)

color_mode(mode, max1, max2, max3)

color_mode(mode, max1, max2, max3, maxA)

## Parameters

| Input | Description |
|-------|-------------|
| mode	(int) | Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness |
| max	(float) | range for all color elements |
| max1	(float) | range for the red or hue depending on the current color mode |
| max2	(float) | range for the green or saturation depending on the current color mode |
| max3	(float) | range for the blue or brightness depending on the current color mode |
| maxA	(float) | range for the alpha |

## Return

pass

## Related

- [background()](/docs/api/color/setting/background_.md)
- [fill()](/docs/api/color/setting/fill_.md)
- [stroke()](/docs/api/color/setting/stroke_.md)