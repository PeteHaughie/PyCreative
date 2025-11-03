"""
// P_2_1_2_01.pde
// 
// Generative Gestaltung, ISBN: 978-3-87439-759-9
// First Edition, Hermann Schmidt, Mainz, 2009
// Hartmut Bohnacker, Benedikt Gross, Julia Laub, Claudius Lazzeroni
// Copyright 2009 Hartmut Bohnacker, Benedikt Gross, Julia Laub, Claudius Lazzeroni
//
// http://www.generative-gestaltung.de
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * changing size and position of circles in a grid
 * 	 
 * MOUSE
 * position x          : circle position
 * position y          : circle size
 * left click          : random position
 * 
 * KEYS
 * s                   : save png
 */
"""


class Sketch:
    def setup(self):
        self.size(600, 600)
        self.window_title("P_2_1_2_01")
        self.tile_count = 20
        self.circle_color = 0
        self.circle_alpha = 10
        self.act_random_seed = 0

    def draw(self):
        self.background(255)

        self.translate(self.width / self.tile_count / 2, self.height / self.tile_count / 2)
        self.no_fill()
        self.random_seed(self.act_random_seed)
        self.stroke(self.circle_color, self.circle_alpha)
        self.stroke_weight(self.mouse_y / 60)

        for grid_y in range(self.tile_count):
            for grid_x in range(self.tile_count):

                pos_x = self.width / self.tile_count * grid_x
                pos_y = self.height / self.tile_count * grid_y

                shift_x = self.random(-self.mouse_x, self.mouse_x) / 20
                shift_y = self.random(-self.mouse_x, self.mouse_x) / 20

                self.circle(pos_x + shift_x, pos_y + shift_y, self.mouse_y / 15)

    def mouse_pressed(self):
        self.act_random_seed = int(self.random(100000))

    def key_released(self):
        if self.key in ('s', 'S'):
            self.save_frame("P_2_1_2_01_##.png")
