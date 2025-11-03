"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/01_P/P_1_0_01/P_1_0_01.pde

P_1_0_01.pde

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
 * changing colors and size by moving the mouse
 *
 * MOUSE
 * position x          : size
 * position y          : color
 *
 * KEYS
 * s                   : save png
 * p                   : save pdf // not implemented in PyCreative
 */

"""


class Sketch:
    def setup(self):
        self.size(720, 720)
        self.window_title("P_1_0_01")
        self.color_mode("HSB", 360, 100, 100)
        self.rect_mode("CENTER")
        self.no_cursor()
        self.no_stroke()
        self.y = 0
        self.x = 0

    def draw(self):
        self.y = self.mouse_y // 2
        self.background(self.y, 100, 100)
        self.fill(360 - self.mouse_y // 2, 100, 100)
        self.rect(360, 360, self.mouse_x + 1, self.mouse_x + 1)

    def key_pressed(self):
        if self.key == 's':
            self.save_frame("P_1_0_01.png")
