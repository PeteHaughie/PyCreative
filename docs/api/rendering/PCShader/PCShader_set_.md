[docs](/docs/)→[api](/docs/api)→[rendering](/docs/api/rendering)→[PCShader()](/docs/api/rendering/PCShader/PCShader_.md)→[PCShader.set()](/docs/api/rendering/PCShader/PCShader_set_.md)

# set()

## Class

PCShader

## Description

Sets the uniform variables inside the shader to modify the effect while the program is running.

Syntax
.set(name, x)	
.set(name, x, y)	
.set(name, x, y, z)	
.set(name, x, y, z, w)	
.set(name, vec)	
.set(name, vec, ncoords)	
.set(name, boolvec, ncoords)	
.set(name, mat)	
.set(name, mat, use3x3)	
.set(name, tex)	

## Parameters

| Input | Description |
|-------|-------------|
| name	(String) | the name of the uniform variable to modify |
| x	(int, float, boolean) | first component of the variable to modify |
| y	(int, float, boolean) | second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2) |
| z	(int, float, boolean) | third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3) |
| w	(int, float, boolean) | fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4) |
| vec	(PVector, int[], float[], boolean[]) | modifies all the components of an array/vector uniform variable. PVector can only be used if the type of the variable is vec3. |
| ncoords	(int) | number of coordinates per element, max 4 |
| mat	(PMatrix2D, PMatrix3D) | matrix of values |
| use3x3	(boolean) | enforces the matrix is 3 x 3 |
| tex	(PImage) | sets the sampler uniform variable to read from this image texture |

## Return

None