"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/01_P/P_2_0_02/P_2_0_02.pde

P_2_0_02.pde

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
 * del, backspace      : erase
 * s                   : save png
 */
"""


class Sketch:
    def setup(self):
        self.size(720, 720)
        self.window_title("P_2_0_02")
        self.no_fill()
        self.no_cursor()
        self.background(255)  # white background
        self.mouse_is_pressed = False

    def draw(self):
        self.translate(self.width / 2, self.height / 2)
        if self.mouse_is_pressed:
            circle_resolution = int(self.map(self.mouse_y + 100, 0, self.height, 2, 10))
            radius = self.mouse_x - self.width / 2 + 0.5
            angle = (self.TWO_PI) / circle_resolution

            self.stroke_weight(2)
            self.stroke(0, 25)

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
            self.save_frame("P_2_0_02_##.png")
            print("saved frame")
        elif self.key == 'backspace':
            self.background(255)
        elif self.key == 'delete':
            self.background(255)