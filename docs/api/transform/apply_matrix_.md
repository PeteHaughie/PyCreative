[docs](/docs/)→[api](/docs/api)→[transform](/docs/api/transform/)→[apply_matrix()](/docs/api/transform/apply_matrix_.md)

# apply_matrix()

## Description

Multiplies the current matrix by the one specified through the parameters. This is very slow because it will try to calculate the inverse of the transform, so avoid it whenever possible. The equivalent function in OpenGL is `glMultMatrix()`.

## Examples

```py
def setup(self):
    self.size(400, 400)
    self.no_fill()
    self.translate(200, 200, 0)
    self.rotateY(self.PI / 6)
    self.stroke(153)
    self.box(140)
    # Set rotation angles
    ct = self.cos(self.PI / 9.0)
    st = self.sin(self.PI / 9.0)
    # Matrix for rotation around the Y axis
    self.apply_matrix(
        ct, 0.0, st, 0.0,
        0.0, 1.0, 0.0, 0.0,
        -st, 0.0, ct, 0.0,
        0.0, 0.0, 0.0, 1.0
    )
    self.stroke(255)
    self.box(200)
```

## Syntax

applyMatrix(source)

applyMatrix(n00, n01, n02, n10, n11, n12)

applyMatrix(n00, n01, n02, n03, n10, n11, n12, n13, n20, n21, n22, n23, n30, n31, n32, n33)

## Parameters

| Input | Description |
|-------|-------------|
| n00	(float) | numbers which define the 4x4 matrix to be multiplied |
| n01	(float) | numbers which define the 4x4 matrix to be multiplied |
| n02	(float) | numbers which define the 4x4 matrix to be multiplied |
| n10	(float) | numbers which define the 4x4 matrix to be multiplied |
| n11	(float) | numbers which define the 4x4 matrix to be multiplied |
| n12	(float) | numbers which define the 4x4 matrix to be multiplied |
| n03	(float) | numbers which define the 4x4 matrix to be multiplied |
| n13	(float) | numbers which define the 4x4 matrix to be multiplied |
| n20	(float) | numbers which define the 4x4 matrix to be multiplied |
| n21	(float) | numbers which define the 4x4 matrix to be multiplied |
| n22	(float) | numbers which define the 4x4 matrix to be multiplied |
| n23	(float) | numbers which define the 4x4 matrix to be multiplied |
| n30	(float) | numbers which define the 4x4 matrix to be multiplied |
| n31	(float) | numbers which define the 4x4 matrix to be multiplied |
| n32	(float) | numbers which define the 4x4 matrix to be multiplied |
| n33	(float) | numbers which define the 4x4 matrix to be multiplied | 

## Return

None

## Related

- [apply_matrix()](/docs/api/transform/apply_matrix_.md)
- [pop_matrix()](/docs/api/transform/pop_matrix_.md)
- [print_matrix()](/docs/api/transform/print_matrix_.md)
- [push_matrix()](/docs/api/transform/push_matrix_.md)
- [reset_matrix()](/docs/api/transform/reset_matrix_.md)
- [rotate_x()](/docs/api/transform/rotate_x_.md)
- [rotate_y()](/docs/api/transform/rotate_y_.md)
- [rotate_z()](/docs/api/transform/rotate_z_.md)
- [rotate()](/docs/api/transform/rotate_.md)
- [scale()](/docs/api/transform/scale_.md)
- [shear_x()](/docs/api/transform/shear_x_.md)
- [shear_y()](/docs/api/transform/shear_y_.md)
- [translate()](/docs/api/transform/translate_.md)