"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/01_P/P_2_1_1/P_2_1_1_01/P_2_1_1_01.pde

P_2_1_1_01.pde

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
 * changing strokeweight and strokecaps on diagonals in a grid
 * 	 
 * MOUSE
 * position x          : left diagonal strokeweight
 * position y          : right diagonal strokeweight
 * left click          : new random layout
 * 
 * KEYS
 * 1                   : round strokecap
 * 2                   : square strokecap
 * 3                   : project strokecap
 * s                   : save png
 */
"""


class Sketch:
    def setup(self):
        self.size(600, 600)
        self.window_title("P_2_1_1_01")
        self.tile_count = 20
        self.act_random_seed = 0
        self.act_stroke_cap = "ROUND"
        self.stroke(0)

    def draw(self):
        self.background(255)
        # self.smooth() unimplemented
        self.no_fill()
        self.stroke_cap(self.act_stroke_cap)

        self.random_seed(self.act_random_seed)

        for grid_y in range(self.tile_count):
            for grid_x in range(self.tile_count):
                pos_x = self.width / self.tile_count * grid_x
                pos_y = self.height / self.tile_count * grid_y

                toggle = int(self.uniform(0, 2))

                if toggle == 0:
                    self.stroke_weight(self.mouse_x / 20)
                    self.line(pos_x, pos_y, pos_x + self.width / self.tile_count, pos_y + self.height / self.tile_count)
                if toggle == 1:
                    self.stroke_weight(self.mouse_y / 20)
                    self.line(pos_x, pos_y + self.width / self.tile_count, pos_x + self.height / self.tile_count, pos_y)
        self.no_loop()

    def mouse_released(self):
        self.act_random_seed = int(self.uniform(0, 100000))
        self.loop()

    def key_released(self):
        if self.key == 's' or self.key == 'S':
            self.save_frame("P_2_1_1_01_##.png")

        if self.key == '1':
            self.act_stroke_cap = "ROUND"
        if self.key == '2':
            self.act_stroke_cap = "SQUARE"
        if self.key == '3':
            self.act_stroke_cap = "PROJECT"