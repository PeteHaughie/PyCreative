"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/01_P/P_2_0_01/P_2_0_01.pde

P_2_0_01.pde

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
 * drawing a filled circle with lines.
 * 	 
 * MOUSE
 * position x          : length
 * position y          : thickness and number of lines
 * 
 * KEYS
 * s                   : save png
 */
"""


class Sketch:
    def setup(self):
        self.size(550, 550)
        self.window_title("P_2_0_01")
        self.no_fill()
        self.stroke(0, 0, 0)
        self.stroke_cap('SQUARE')
        self.no_cursor()

    def draw(self):
        self.background(255)
        self.translate(self.width / 2, self.height / 2)

        circle_resolution = int(self.map(self.mouse_y, 0, self.height, 2, 80))
        radius = self.mouse_x - self.width / 2 + 0.5
        angle = (self.TWO_PI * 2) / circle_resolution 

        self.stroke_weight(self.mouse_y / 20)

        self.begin_shape()
        for i in range(circle_resolution + 1):
            x = self.cos(angle * i) * radius
            y = self.sin(angle * i) * radius
            self.line(0, 0, x, y)
            # vertex(x, y);
        self.end_shape()

    def key_pressed(self):
        if self.key == 's' or self.key == 'S':
            self.save_frame("P_2_0_01.png")
