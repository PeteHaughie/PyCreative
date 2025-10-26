[docs](/docs/)→[api](/docs/api)→[rendering](/docs/api/rendering)→[shaders](/docs/api/rendering/shaders)→[load_shader()](/docs/api/rendering/shaders/load_shader_.md)

# load_shader()

## Description

Loads a shader into the PCShader object. The shader file must be loaded in the sketch's `data` folder/directory to load correctly.

If the file is not available or an error occurs, null will be returned and an error message will be printed to the console.

## Examples

```py
def setup(self):
    self.size(640, 360)
    # Shaders files must be in the "data" folder to load correctly
    self.blur = self.load_shader("blur.glsl")
    self.stroke(0, 102, 153)
    self.rect_mode("CENTER")

def draw(self):
    self.filter(self.blur)
    self.rect(self.mouseX-75, self.mouseY, 150, 150)
    self.ellipse(self.mouseX+75, self.mouseY, 150, 150)
```

## Syntax

load_shader(frag_filename)

load_shader(frag_filename, vert_filename)	

## Parameters

| Input | Description |
|-------|-------------|
| frag_filename	(String) | name of fragment shader file |
| vert_filename	(String) | name of vertex shader file |

## Return

PCShader

## Related

- [shader()](/docs/api/rendering/shaders/shader_.md)
- [resetShader()](/docs/api/rendering/shaders/reset_shader_.md)