"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/01_P/P_1_1_1_01/P_1_1_1_01.pde

P_1_1_1_01.pde

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
 * draw the color spectrum by moving the mouse
 * 	 
 * MOUSE
 * position x/y        : resolution
 * 
 * KEYS
 * s                   : save png
 * p                   : save pdf // not implemented in PyCreative
 */
"""


class Sketch:
    def setup(self):
        self.size(800, 400)
        self.window_title("P_1_1_1_01")
        self.color_mode("HSB", self.width, self.height, 100)
        self.no_stroke()
        self.step_x = 0
        self.step_y = 0

    def draw(self):
        self.background(0)
        self.step_x = self.mouse_x + 2
        self.step_y = self.mouse_y + 2

        for grid_y in range(0, self.height, self.step_y):
            for grid_x in range(0, self.width, self.step_x):
                self.fill(grid_x, self.height - grid_y, 100)
                self.rect(grid_x, grid_y, self.step_x, self.step_y)

    def key_pressed(self):
        if self.key == 's':
            self.save_frame("P_1_1_1_01.png")
