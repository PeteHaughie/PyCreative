"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/01_P/P_1_1_2_01/P_1_1_2_01.pde

P_1_1_2_01.pde

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
 * changing the color circle by moving the mouse.
 * 	 
 * MOUSE
 * position x          : saturation
 * position y          : brighness
 * 
 * KEYS
 * 1-5                 : number of segments
 * s                   : save png
 */
"""

class Sketch:
    def setup(self):
        self.size(800, 800)
        self.window_title("P_1_1_2_01")
        # Use canvas width/height for saturation/brightness ranges so
        # mouse_x/mouse_y map naturally across the drawing area.
        self.color_mode('HSB', 360, self.width, self.height)
        self.no_stroke()
        self.segment_count = 360
        self.radius = 300

    def draw(self):
        self.background(0, 0, 100)
        angle_step = 360.0 / float(self.segment_count)
        self.begin_shape("TRIANGLE_FAN")
        self.vertex(self.width / 2, self.height / 2)
        # iterate by integer steps and compute the angle per-step
        for i in range(self.segment_count + 1):
            angle = i * angle_step
            vx = self.width / 2 + self.cos(self.radians(angle)) * self.radius
            vy = self.height / 2 + self.sin(self.radians(angle)) * self.radius
            # Use canvas center as fallback when running headless (mouse defaults to 0)
            mx = self.mouse_x or (self.width / 2)
            my = self.mouse_y or (self.height / 2)
            # Processing idiom: call fill before vertex
            self.fill(angle, mx, my)
            self.vertex(vx, vy)
        self.end_shape()

    def key_pressed(self):
        if self.key == 's':
            self.save_frame("P_1_1_2_01.png")
        elif self.key in ['1', '2', '3', '4', '5']:
            if self.key == '1':
                self.segment_count = 360
            elif self.key == '2':
                self.segment_count = 45
            elif self.key == '3':
                self.segment_count = 24
            elif self.key == '4':
                self.segment_count = 12
            elif self.key == '5':
                self.segment_count = 6
