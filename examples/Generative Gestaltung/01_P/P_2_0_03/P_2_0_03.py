"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/01_P/P_2_0_03/P_2_0_03.pde

P_2_0_03.pde

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
 * drawing with a changing shape by draging the mouse.
 * 	 
 * MOUSE
 * position x          : length
 * position y          : thickness and number of lines
 * drag                : draw
 * 
 * KEYS
 * 1-3                 : stroke color
 * del, backspace      : erase
 * s                   : save png
 */
"""


class Sketch:
    def setup(self):
        self.size(720, 720)
        self.window_title("P_2_0_03")
        self.no_fill()
        self.color_mode('HSB', 360, 100, 100)
        self.mouse_is_pressed = False
        self.stroke_color = (0, 0, 0, 10)
        self.background(0, 0, 100)  # white background
        self.no_cursor()

    def draw(self):
        self.translate(self.width / 2, self.height / 2)
        if self.mouse_is_pressed:
            circle_resolution = int(self.map(self.mouse_y + 100, 0, self.height, 2, 10))
            radius = self.mouse_x - self.width / 2 + 0.5
            angle = (self.TWO_PI) / circle_resolution

            self.stroke_weight(2)
            self.stroke(self.stroke_color)

            self.begin_shape()
            for i in range(circle_resolution + 1):
                x = 0 + (self.cos(angle * i) * radius)
                y = 0 + (self.sin(angle * i) * radius)
                self.vertex(x, y)
            self.end_shape()
    
    def mouse_pressed(self):
        self.mouse_is_pressed = True

    def mouse_released(self):
        self.mouse_is_pressed = False

    def key_released(self):
        if self.key == 's' or self.key == 'S':
            self.save_frame("P_2_0_03_##.png")
        elif self.key == 'backspace':
            self.background(255)
        elif self.key == 'delete':
            self.background(255)
        elif self.key in ('1', '2', '3'):
            if self.key == '1':
                self.stroke_color = (0, 0, 0, 10)
            elif self.key == '2':
                self.stroke_color = (192, 100, 64, 10)
            elif self.key == '3':
                self.stroke_color = (52, 100, 71, 10)