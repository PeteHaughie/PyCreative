[docs](/docs/)→[api](/docs/api)→[math](/docs/api/math/)→[PCVector](/docs/api/math/PCVector/PCVector.md)

# PCVector

## Description

A class to describe a two or three dimensional vector, specifically a Euclidean (also known as geometric) vector. A vector is an entity that has both magnitude and direction. The datatype, however, stores the components of the vector (x,y for 2D, and x,y,z for 3D). The magnitude and direction can be accessed via the methods `mag()` and `heading()`.

In many of the PyCreative examples, you will see `PCVector` used to describe a position, velocity, or acceleration. For example, if you consider a rectangle moving across the screen, at any given instant it has a position (a vector that points from the origin to its location), a velocity (the rate at which the object's position changes per time unit, expressed as a vector), and acceleration (the rate at which the object's velocity changes per time unit, expressed as a vector). Since vectors represent groupings of values, we cannot simply use traditional addition/multiplication/etc. Instead, we'll need to do some "vector" math, which is made easy by the methods inside the `PCVector` class.

## Examples

```py
def setup(self):
    self.size(200, 200)
    self.v1 = self.pcvector(40, 20)
    self.v2 = self.pcvector(25, 50)

def draw(self):
    self.background(255)
    self.fill(0)
    self.circle(self.v1.x, self.v1.y, 12)
    self.circle(self.v2.x, self.v2.y, 12)
    self.v2.add(self.v1)
    self.circle(self.v2.x, self.v2.y, 24)
```

## Constructors

PCVector()

PCVector(x, y)

PCVector(x, y, z)

## Fields

| Field | Description |
|-------|-------------|
| [x](/docs/api/math/PCVector/PCVector_x.md) | The x component of the vector |
| [y](/docs/api/math/PCVector/PCVector_y.md) | The y component of the vector |
| [z](/docs/api/math/PCVector/PCVector_z.md) | The z component of the vector | 

## Parameters

| Parameter | Description |
|-----------|-------------|
| x (float) | The x coordinate |
| y (float) | The y coordinate |
| z (float) | The z coordinate |

## Methods

-[set()](/PCVector_set_.md)	Set the components of the vector
-[random2d()](/docs/api/math/PCVector/PCVector_random2d_.md)	Make a new 2D unit vector with a random direction
-[random3d()](/docs/api/math/PCVector/PCVector_random3d_.md)	Make a new 3D unit vector with a random direction
-[from_angle()](/docs/api/math/PCVector/PCVector_from_angle_.md)	Make a new 2D unit vector from an angle
-[copy()](/docs/api/math/PCVector/PCVector_copy_.md)	Get a copy of the vector
-[mag()](/docs/api/math/PCVector/PCVector_mag_.md)	Calculate the magnitude of the vector
-[mag_sq()](/docs/api/math/PCVector/PCVector_mag_sq_.md)	Calculate the magnitude of the vector, squared
-[add()](/docs/api/math/PCVector/PCVector_add_.md)	Adds x, y, and z components to a vector, one vector to another, or two independent vectors
-[sub()](/docs/api/math/PCVector/PCVector_sub_.md)	Subtract x, y, and z components from a vector, one vector from another, or two independent vectors
-[mult()](/docs/api/math/PCVector/PCVector_mult_.md)	Multiply a vector by a scalar
-[div()](/docs/api/math/PCVector/PCVector_div_.md)	Divide a vector by a scalar
-[dist()](/docs/api/math/PCVector/PCVector_dist_.md)	Calculate the distance between two points
-[dot()](/docs/api/math/PCVector/PCVector_dot_.md)	Calculate the dot product of two vectors
-[cross()](/docs/api/math/PCVector/PCVector_cross_.md)	Calculate and return the cross product
-[normalize()](/docs/api/math/PCVector/PCVector_normalize_.md)	Normalize the vector to a length of 1
-[limit()](/docs/api/math/PCVector/PCVector_limit_.md)	Limit the magnitude of the vector
-[set_mag()](/docs/api/math/PCVector/PCVector_set_mag_.md)	Set the magnitude of the vector
-[heading()](/docs/api/math/PCVector/PCVector_heading_.md)	Calculate the angle of rotation for this vector
-[set_heading()](/docs/api/math/PCVector/PCVector_set_heading_.md)	Set the direction for this vector
-[rotate()](/docs/api/math/PCVector/PCVector_rotate_.md)	Rotate the vector by an angle (2D only)
-[lerp()](/docs/api/math/PCVector/PCVector_lerp_.md)	Linear interpolate the vector to another vector
-[angle_between()](/docs/api/math/PCVector/PCVector_angle_between_.md)	Calculate and return the angle between two vectors
-[array()](/docs/api/math/PCVector/PCVector_array_.md)	Return a representation of the vector as a float array