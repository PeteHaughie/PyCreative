"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/01_P/P_1_2_1_01/P_1_2_1_01.pde

P_1_2_1_01.pde

Generative Gestaltung, ISBN: 978-3-87439-759-9
First Edition, Hermann Schmidt, Mainz, 2009
Hartmut Bohnacker, Benedikt Gross, Julia Laub, Claudius Lazzeroni
Copyright 2009 Hartmut Bohnacker, Benedikt Gross, Julia Laub, Claudius Lazzeroni

http://www.generative-gestaltung.de

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

/**
 * shows how to interpolate colors in different styles/ color modes
 * 
 * MOUSE
 * left click          : new random color set
 * position x          : interpolation resolution
 * position y          : row count
 * 
 * KEYS
 * 1-2                 : switch interpolation style
 * s                   : save png
 */
"""


class Sketch:
  def setup(self):
    self.size(800, 800)
    self.window_title("P_1_2_1_01")
    self.color_mode('HSB', 360, 100, 100)
    self.no_stroke()
    self.tile_count_x = 2
    self.tile_count_y = 10
    self.colors_left = [self.color(0, 0, 0) for _ in range(self.tile_count_y)]
    self.colors_right = [self.color(0, 0, 0) for _ in range(self.tile_count_y)]
    self.colors = []
    self.interpolate_shortest = True
    self.shake_colors()

  def draw(self):
    self.tile_count_x = int(self.map(self.mouse_x, 0, self.width, 2, 100))
    self.tile_count_y = int(self.map(self.mouse_y, 0, self.height, 2, 10))
    tile_width = self.width / float(self.tile_count_x)
    tile_height = self.height / float(self.tile_count_y)

    for grid_y in range(self.tile_count_y):
      col1 = self.colors_left[grid_y] # this is choking the sketch
      col2 = self.colors_right[grid_y]

      for grid_x in range(self.tile_count_x):
        amount = self.map(grid_x, 0, self.tile_count_x - 1, 0, 1)
        if self.interpolate_shortest:
          self.color_mode('RGB', 255, 255, 255)
          inter_col = self.lerp_color(col1, col2, amount)
        else:
          self.color_mode('HSB', 360, 100, 100)
          inter_col = self.lerp_color(col1, col2, amount)

        self.fill(inter_col)
        self.rect(tile_width * grid_x, tile_height * grid_y, tile_width, tile_height)
    self.rect(0, 0, 50, 50)  # dummy rect to force flush of shape

  def shake_colors(self):
    for i in range(self.tile_count_y):
      self.colors_left[i] = self.color(self.random(0, 60), self.random(0, 100), 100)
      self.colors_right[i] = self.color(self.random(160, 190), 100, self.random(0, 100))

  def mouse_released(self):
    self.shake_colors()

  def key_released(self):
    if self.key == 's' or self.key == 'S':
      self.save_frame("P_1_2_1_01_##.png")
    if self.key == 'r' or self.key == 'R':
      self.shake_colors()

    if self.key == '1':
      self.interpolate_shortest = True
    if self.key == '2':
      self.interpolate_shortest = False