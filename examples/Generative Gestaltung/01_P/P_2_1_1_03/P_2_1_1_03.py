"""
// P_2_1_1_03.pde
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
 * changing number, color and strokeweight on diagonals in a grid
 * 	 
 * MOUSE
 * position x          : diagonal strokeweight
 * position y          : number diagonals
 * left click          : new random layout
 * 
 * KEYS
 * s                   : save png
 * 1                   : color left diagonal
 * 2                   : color right diagonal
 * 3                   : switch transparency left diagonal on/off
 * 4                   : switch transparency right diagonal on/off
 * 5                   : switch cap style to SQUARE
 * 6                   : switch cap style to PROJECT
 * 7                   : switch cap style to ROUND
 * 0                   : default
 */
"""


class Sketch:
    def setup(self):
        self.size(600, 600)
        self.window_title("P_2_1_1_03")
        self.tile_count = 1
        self.transparent_left = False
        self.transparent_right = False
        self.alpha_left = 100
        self.alpha_right = 100
        self.color_mode("HSB", 360, 100, 100, 100)
        self.color_back = (255, 255, 255)
        self.color_left = (323, 100, 77)
        self.color_right = (0, 0, 0)
        self.act_random_seed = 0
        self.no_fill()
        self.no_cursor()

    def draw(self):
        self.background(self.color_back)
        self.random_seed(self.act_random_seed)
        self.stroke_weight(self.mouse_x / 15)
        self.tile_count = int(self.mouse_y / 15)

        for grid_y in range(self.tile_count):
            for grid_x in range(self.tile_count):

                pos_x = self.width / self.tile_count * grid_x
                pos_y = self.height / self.tile_count * grid_y

                if self.transparent_left:
                    self.alpha_left = grid_y * 10
                else:
                    self.alpha_left = 100

                if self.transparent_right:
                    self.alpha_right = 100 - grid_y * 10
                else:
                    self.alpha_right = 100

                toggle = int(self.random(0, 2))

                if toggle == 0:
                    self.stroke(*self.color_left, self.alpha_left)
                    self.line(pos_x, pos_y, pos_x + (self.width / self.tile_count) / 2, pos_y + self.height / self.tile_count)
                    self.line(pos_x + (self.width / self.tile_count) / 2, pos_y, pos_x + (self.width / self.tile_count), pos_y + self.height / self.tile_count)
                if toggle == 1:
                    self.stroke(*self.color_right, self.alpha_right)
                    self.line(pos_x, pos_y + self.width / self.tile_count, pos_x + (self.height / self.tile_count) / 2, pos_y)
                    self.line(pos_x + (self.height / self.tile_count) / 2, pos_y + self.width / self.tile_count, pos_x + (self.height / self.tile_count), pos_y)

    def mouse_pressed(self):
        self.act_random_seed = int(self.random(0, 100000))

    def key_released(self):
        if self.key == 's' or self.key == 'S':
            self.save_frame("P_2_1_1_03_##.png")

        if self.key == '1':
            if self.color_left == (273, 73, 51):
                self.color_left = (323, 100, 77)
            else:
                self.color_left = (273, 73, 51)
                #      colorLeft = color(0);

        if self.key == '2':
            if self.color_right == (0, 0, 0):
                self.color_right = (192, 100, 64)
            else:
                self.color_right = (0, 0, 0)

        if self.key == '3':
            self.transparent_left = not self.transparent_left

        if self.key == '4':
            self.transparent_right = not self.transparent_right

        if self.key == '0':
            self.transparent_left = False
            self.transparent_right = False
            self.color_left = (323, 100, 77)
            self.color_right = (0, 0, 0)
