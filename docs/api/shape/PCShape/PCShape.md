[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)

# PCShape

## Description

Datatype for storing shapes. Before a shape is used, it must be loaded with the `load_shape()` or created with the `create_shape()`. The `shape()` function is used to draw the shape to the display window. The `load_Shape()` function supports SVG files created with Inkscape and Adobe Illustrator. It is not a full SVG implementation, but offers some straightforward support for handling vector data.

The `PCShape` object contains a group of methods that can operate on the shape data.

To create a new shape, use the `create_shape()` function. Do not use the syntax new `PCShape()`.

## Examples

```py
def setup(self):
  self.size(100, 100)
  # Creating the PCShape as a square. The corner
  # is 0,0 so that the center is at 40,40
  self.square = self.create_shape("RECT", 0, 0, 80, 80)

def draw(self):
  self.shape(self.square, 10, 10)
```

```py
def setup(self):
  self.size(400, 400)
  # The file "bot.svg" must be in the data folder
  # of the current sketch to load successfully
  self.s = load_shape("bot.svg")

def draw(self):
  self.shape(s, 40, 40, 320, 320)
```

## Constructors

PCShape(g, kind, params)

## Fields

| Field                                               | Description           |
| --------------------------------------------------- | --------------------- |
| [width](/docs/api/shape/PCShape/PCShape_width.md)   | Shape document width  |
| [height](/docs/api/shape/PCShape/PCShape_height.md) | Shape document height |

## Methods

| Method | Description |
|--------|-------------|
| [is_visible()](/docs/api/shape/PCShape/PCShape_is_visible_.md) | Returns a boolean value true if the image is set to be visible, false if not |
| [set_visible()](/docs/api/shape/PCShape/PCShape_set_visible_.md) | Sets the shape to be visible or invisible |
| [disable_style()](/docs/api/shape/PCShape/PCShape_disable_style_.md) | Disables the shape's style data and uses PyCreative styles |
| [enable_style()](/docs/api/shape/PCShape/PCShape_enable_style_.md) | Enables the shape's style data and ignores the PyCreative styles |
| [begin_contour()](/docs/api/shape/PCShape/PCShape_begin_contour_.md) | Starts a new contour |
| [end_contour()](/docs/api/shape/PCShape/PCShape_end_contour_.md) | Ends a contour |
| [begin_shape()](/docs/api/shape/PCShape/PCShape_begin_shape_.md) | Starts the creation of a new PShape |
| [end_shape()](/docs/api/shape/PCShape/PCShape_end_shape_.md) | Finishes the creation of a new PShape |
| [get_child_count()](/docs/api/shape/PCShape/PCShape_get_child_count_.md) | Returns the number of children |
| [get_child()](/docs/api/shape/PCShape/PCShape_get_child_.md) | Returns a child element of a shape as a PShape object |
| [add_child()](/docs/api/shape/PCShape/PCShape_add_child_.md) | Adds a new child |
| [get_vertex_count()](/docs/api/shape/PCShape/PCShape_get_vertex_count_.md) | Returns the total number of vertices as an int |
| [get_vertex()](/docs/api/shape/PCShape/PCShape_get_vertex_.md) | Returns the vertex at the index position |
| [set_vertex()](/docs/api/shape/PCShape/PCShape_set_vertex_.md) | Sets the vertex at the index position |
| [set_fill()](/docs/api/shape/PCShape/PCShape_set_fill_.md) | Set the fill value |
| [set_stroke()](/docs/api/shape/PCShape/PCShape_set_stroke_.md) | Set the stroke value |
| [translate()](/docs/api/shape/PCShape/PCShape_translate_.md) | Displaces the shape |
| [rotate_x()](/docs/api/shape/PCShape/PCShape_rotate_x_.md) | Rotates the shape around the x‑axis |
| [rotate_y()](/docs/api/shape/PCShape/PCShape_rotate_y_.md) | Rotates the shape around the y‑axis |
| [rotate_z()](/docs/api/shape/PCShape/PCShape_rotate_z_.md) | Rotates the shape around the z‑axis |
| [rotate()](/docs/api/shape/PCShape/PCShape_rotate_.md) | Rotates the shape |
| [scale()](/docs/api/shape/PCShape/PCShape_scale_.md) | Increases and decreases the size of a shape |
| [reset_matrix()](/docs/api/shape/PCShape/PCShape_reset_matrix_.md) | Replaces the current matrix of a shape with the identity matrix |
