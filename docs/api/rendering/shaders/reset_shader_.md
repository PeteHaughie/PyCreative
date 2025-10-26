[docs](/docs/)→[api](/docs/api)→[rendering](/docs/api/rendering)→[shaders](/docs/api/rendering/shaders)→[reset_shader()](/docs/api/rendering/shaders/reset_shader_.md)

# reset_shader()

## Description

Restores the default shaders. Code that runs after `reset_shader()` will not be affected by previously defined shaders.

## Examples

```py
def setup(self):
    self.size(640, 360)
    self.img = self.load_image("leaves.jpg")
    self.edges = self.load_shader("edges.glsl")

def draw(self):
    self.shader(self.edges)
    self.image(self.img, 0, 0)
    self.reset_shader()
    self.image(self.img, self.width/2, 0)
```

## Syntax

reset_shader()	

## Return

None

## Related

- [shader()](/docs/api/rendering/shaders/shader_.md)
- [loadShader()](/docs/api/rendering/shaders/load_shader_.md)