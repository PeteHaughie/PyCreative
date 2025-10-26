[docs](/docs/)→[api](/docs/api)→[rendering](/docs/api/rendering)→[PCShader()](/docs/api/rendering/PCShader/PCShader_.md)

# PCShader

## Description

This class encapsulates a `GLSL` shader program, including a vertex and a fragment shader. Use the `load_shader()` function to load your shader code. Note: It's strongly encouraged to use `load_shader()` to create a `PCShader` object, rather than calling the PCShader constructor manually.

## Examples

```py
def setup(self):
    self.size(640, 360, "P2D")
    # Shaders files must be in the "data" folder to load correctly
    self.blur = self.load_shader("blur.glsl")
    self.stroke(0, 102, 153)
    self.rect_mode("CENTER")

def draw(self):
    self.filter(self.blur)
    self.rect(self.mouse_x-75, self.mouse_y, 150, 150)
    self.ellipse(self.mouse_x+75, self.mouse_y, 150, 150)
```

```py
def setup(self):
    self.size(640, 360, "P2D")
    self.tex = self.load_image("tex1.jpg")
    self.deform = self.load_shader("deform.glsl")
    self.deform.set("resolution", float(self.width), float(self.height))

def draw(self):
    self.deform.set("time", self.millis() / 1000.0)
    self.deform.set("mouse", float(self.mouse_x), float(self.mouse_y))
    self.shader(self.deform)
    self.image(self.tex, 0, 0, self.width, self.height)
```

## Constructors

PShader()	

PShader(parent)	

PShader(parent, vert_filename, frag_filename)	

PShader(parent, vert_url, frag_url)	

PShader(parent, vert_source, frag_source)	

## Parameters

| Input | Description |
|-------|-------------|
| parent (Engine) | the parent Engine or sketch instance |
| vert_filename (str) | name of the vertex shader file |
| frag_filename (str) | name of the fragment shader file |
| vert_url (str) | network location of the vertex shader |
| frag_url (str) | network location of the fragment shader |

## Methods

[set()](/docs/api/rendering/PCShader/PCShader_set_.md)	Sets a variable within the shader 
