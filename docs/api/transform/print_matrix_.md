[docs](/docs/)→[api](/docs/api)→[transform](/docs/api/transform/)→[print_matrix()](/docs/api/transform/print_matrix_.md)

# print_matrix()

## Description

Prints the current matrix to the console

### Example

```py
size(100, 100)
self.print_matrix()
# Prints:
# 01.0000  00.0000  00.0000 -50.0000
# 00.0000  01.0000  00.0000 -50.0000
# 00.0000  00.0000  00.0000 -86.6025
# 00.0000  00.0000  00.0000  01.0000

self.reset_matrix()
self.print_matrix()
# Prints:
# 1.0000  0.0000  0.0000  0.0000
# 0.0000  1.0000  0.0000  0.0000
# 0.0000  0.0000  1.0000  0.0000
# 0.0000  0.0000  0.0000  1.0000
``` 

## Syntax

printMatrix()

## Return

None

## Related

- [push_matrix()](/docs/api/transform/push_matrix_.md)
- [pop_matrix()](/docs/api/transform/pop_matrix_.md)
- [reset_matrix()](/docs/api/transform/reset_matrix_.md)
- [apply_matrix()](/docs/api/transform/apply_matrix_.md)