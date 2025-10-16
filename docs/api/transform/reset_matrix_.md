[docs](/docs/)→[api](/docs/api)→[transform](/docs/api/transform/)→[reset_matrix()](/docs/api/transform/reset_matrix_.md)

# reset_matrix()

## Description

Replaces the current matrix with the identity matrix. The equivalent function in OpenGL is `glLoadIdentity()`.

### Example

```py
self.size(400, 400)
self.no_fill()
self.box(320)
self.print_matrix()
# Prints:
# 001.0000  000.0000  000.0000 -200.0000
# 000.0000  001.0000  000.0000 -200.0000
# 000.0000  000.0000  001.0000 -346.4102
# 000.0000  000.0000  000.0000  001.0000

self.reset_matrix()
self.box(320)
self.print_matrix()
# Prints:
# 1.0000  0.0000  0.0000  0.0000
# 0.0000  1.0000  0.0000  0.0000
# 0.0000  0.0000  1.0000  0.0000
# 0.0000  0.0000  0.0000  1.0000
```

## Syntax

resetMatrix()

## Return

None

## Related

- [push_matrix()](/docs/api/transform/push_matrix_.md)
- [pop_matrix()](/docs/api/transform/pop_matrix_.md)
- [apply_matrix()](/docs/api/transform/apply_matrix_.md)
- [print_matrix()](/docs/api/transform/print_matrix_.md)