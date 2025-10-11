[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[constants](/docs/api/constants/)

# TWO_PI

## Description

TWO_PI is a mathematical constant with the value 6.2831853. It is twice the ratio of the circumference of a circle to its diameter. It is useful in combination with the trigonometric functions `sin()` and `cos()`.

## Examples

```py
float x = self.width/2
float y = self.height/2
float d = self.width * 0.8
self.size(400,400)
self.arc(x, y, d, d, 0, self.QUARTER_PI)
self.arc(x, y, d-80, d-80, 0, self.HALF_PI)
self.arc(x, y, d-160, d-160, 0, self.PI)
self.arc(x, y, d-240, d-240, 0, self.TWO_PI)
```

## Related

- [PI](/docs/api/constants/PI.md)
- [HALF_PI](/docs/api/constants/HALF_PI.md)
- [TAU](/docs/api/constants/TAU.md)
- [QUARTER_PI](/docs/api/constants/QUARTER_PI.md)
