[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[random](/docs/api/math/random/)

# random()

## Description


Generates random numbers. Each time the `random()` function is called, it returns an unexpected value within the specified range. If only one parameter is passed to the function, it will return a float between zero and the value of the high parameter. For example, `random(5)` returns values between 0 and 5 (starting at zero, and up to, but not including, 5).

If two parameters are specified, the function will return a float with a value between the two values. For example, `random(-5, 10.2)` returns values starting at -5 and up to (but not including) 10.2. To convert a floating-point random number to an integer, use the `int()` function.

## Examples

```py
for i in range(100):
  r = self.random()
  self.stroke(r * 255)
  self.line(50, i, 50 + r * 100, i)
```

```py
for i in range(100):
  r = self.random(50)
  self.stroke(r * 5)
  self.line(50, i, 50 + r, i)
```

```py
for i in range(100):
  r = self.random(-50, 50)
  print(r)
```

```py
words = ["apple", "bear", "cat", "dog"]
index = int(self.random(len(words)))  # Same as int(random(4))
print(words[index])  # Prints one of the four words
```

## Syntax

random()

random(high)

random(low, high)

## Parameters

| Input | Description |
|-------|-------------|
| none | If no parameters are given, returns a float from 0 (inclusive) to 1 (exclusive) |
| low (float) | The lower limit (inclusive) of the random number to be generated |
| high (float) | The upper limit (exclusive) of the random number to be generated |

## Return

float

## Related

- [random_seed()](/docs/api/math/random/random_seed_.md)
- [noise()](/docs/api/math/random/noise_.md)