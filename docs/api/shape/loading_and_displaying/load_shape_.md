[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[attributes](/docs/api/shape/attributes/)→[loading_and_displaying](/docs/api/shape/loading_and_displaying/)

# load_shape()

## Description

Loads geometry into a variable of type PCShape. SVG and OBJ files may be loaded. To load correctly, the file must be located in the data directory of the current sketch. In most cases, `load_shape()` should be used inside `setup()` because loading shapes inside `draw()` will reduce the speed of a sketch.

Alternatively, the file maybe be loaded from anywhere on the local computer using an absolute path (something that starts with / on Unix and Linux, or a drive letter on Windows), or the filename parameter can be a URL for a file found on a network.

If the file is not available or an error occurs, null will be returned and an error message will be printed to the console. The error message does not halt the program, however the null value may cause a NullPointerException if your code does not check whether the value returned is null.

## Examples

```py
def setup(self):
  self.size(400, 400)
  # The file "bot.svg" must be in the data folder
  # of the current sketch to load successfully
  self.s = load_shape("bot.svg")

def draw(self):
  self.shape(self.s, 40, 40, 320, 320)
```

```py
def setup(self):
  self.size(400, 400)
  # The file "bot.obj" must be in the data folder
  # of the current sketch to load successfully
  self.s = load_shape("bot.obj")

def draw(self):
  self.background(204)
  self.translate(self.width/2, self.height/2)
  self.shape(self.s, 0, 0)
```

## Syntax

load_shape(filename)	

## Parameters

| Input    | Description                     |
|----------|---------------------------------|
| filename (String) | name of file to load, can be .svg or .obj |

## Return

PCShape	

## Related

- [PCShape](/docs/api/shape/PCShape/PCShape.md)
- [create_shape()](/docs/api/shape/PCShape/PCShape_create_shape_.md)