[docs](/docs/)→[api](/docs/api)→[transform](/docs/api/transform/)→[push_matrix()](/docs/api/transform/push_matrix_.md)

# push_matrix()

## Description

Pushes the current transformation matrix onto the matrix stack. Understanding pushing and popping requires understanding the concept of a matrix stack. The `push_matrix()` function saves the current coordinate system to the stack and `pop_matrix()` restores the prior coordinate system. `push_matrix()` and `pop_matrix()` are used in conjunction with the other transformation functions and may be embedded to control the scope of the transformations.

### Example

```py
self.size(400, 400)
self.fill(255)
self.rect(0, 0, 200, 200)  # White rectangle
self.push_matrix()
self.translate(120, 80)
self.fill(0)
self.rect(0, 0, 200, 200)  # Black rectangle
self.pop_matrix()
self.fill(100)
self.rect(60, 40, 200, 200)  # Gray rectangle
```

## Syntax

pushMatrix()

## Return

None

## Related

- [pop_matrix()](/docs/api/transform/pop_matrix_.md)