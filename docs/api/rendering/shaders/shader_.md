[docs](/docs/)→[api](/docs/api)→[rendering](/docs/api/rendering)→[shaders](/docs/api/rendering/shaders)→[shader()](/docs/api/rendering/shaders/shader_.md)

# shader()


## Description

Applies the shader specified by the parameters.

## Examples

```py
def setup(self):
    self.size(640, 360)
    self.img = self.load_image("leaves.jpg")
    self.edges = self.load_shader("edges.glsl")

def draw(self):
    self.shader(self.edges)
    self.image(self.img, 0, 0)
```

## Syntax

shader(shader)	

## Parameters

| Input | Description |
|-------|-------------|
| shader	(PCShader) | name of shader file |

## Return

None

## Related

- [loadShader()](/docs/api/rendering/shaders/load_shader_.md)
- [resetShader()](/docs/api/rendering/shaders/reset_shader_.md)