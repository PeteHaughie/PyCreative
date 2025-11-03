"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/01_P/P_2_1_1/P_2_1_1_02/P_2_1_1_02.pde

P_2_1_1_02.pde

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
 * changing strokeweight on diagonals in a grid with colors
 * 	 
 * MOUSE
 * position x          : left diagonal strokeweight
 * position y          : right diagonal strokeweight
 * left click          : new random layout
 * 
 * KEYS
 * s                   : save png
 * 1                   : round strokecap
 * 2                   : square strokecap
 * 3                   : project strokecap
 * 4                   : color left diagonal
 * 5                   : color right diagonal
 * 6                   : transparency left diagonal
 * 7                   : transparency right diagonal
 * 0                   : default
 */
"""


class Sketch:
  def setup(self):
    self.size(600, 600)
    self.window_title("P_2_1_1_02")
    self.color_mode('HSB', 360, 100, 100, 100)  # HSB color mode
    self.background(360, 360, 360)  # white background
    self.no_fill()
    self.act_random_seed = 0
    self.act_stroke_cap = "ROUND"

    self.tile_count = 20

    self.color_left = (197, 0, 123)
    self.color_right = (87, 35, 129)

    self.alpha_left = 100
    self.alpha_right = 100

  def draw(self):
    self.color_mode('HSB', 360, 100, 100)
    self.background(0, 0, 100)
    # self.smooth() unnecessary
    self.no_fill()
    self.stroke_cap(self.act_stroke_cap)

    self.random_seed(self.act_random_seed)

    for grid_y in range(self.tile_count):
      for grid_x in range(self.tile_count):
        pos_x = self.width / self.tile_count * grid_x
        pos_y = self.height / self.tile_count * grid_y

        toggle = int(self.random(0, 2))

        if toggle == 0:
          self.stroke(*self.color_left, self.alpha_left)
          self.stroke_weight(self.mouse_x / 10)
          self.line(pos_x, pos_y, pos_x + self.width / self.tile_count, pos_y + self.height / self.tile_count)
        if toggle == 1:
          self.stroke(*self.color_right, self.alpha_right)
          self.stroke_weight(self.mouse_y / 10)
          self.line(pos_x, pos_y + self.width / self.tile_count, pos_x + self.height / self.tile_count, pos_y)

  def mouse_pressed(self):
    self.act_random_seed = int(self.random(0, 100000))

  def key_released(self):
    if self.key == 's' or self.key == 'S':
      self.save_frame("P_2_1_1_02_##.png")

    if self.key == '1':
      self.act_stroke_cap = "ROUND"
    if self.key == '2':
      self.act_stroke_cap = "SQUARE"
    if self.key == '3':
      self.act_stroke_cap = "PROJECT"

    if self.key == '4':
      if self.color_left == (0, 0, 0):
        self.color_left = (323, 100, 77)
      else:
        self.color_left = (0, 0, 0)

    if self.key == '5':
      if self.color_right == (0, 0, 0):
        self.color_right = (273, 73, 51)
      else:
        self.color_right = (0, 0, 0)

    if self.key == '6':
      if self.alpha_left == 100:
        self.alpha_left = 50
      else:
        self.alpha_left = 100

    if self.key == '7':
      if self.alpha_right == 100:
        self.alpha_right = 50
      else:
        self.alpha_right = 100

    if self.key == '0':
      self.act_stroke_cap = "ROUND"
      self.color_left = (0, 0, 0)
      self.color_right = (0, 0, 0)
      self.alpha_left = 100
      self.alpha_right = 100
