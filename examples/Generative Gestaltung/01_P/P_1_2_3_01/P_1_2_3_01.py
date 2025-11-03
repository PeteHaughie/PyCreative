"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/01_P/P_1_2_3_01/P_1_2_3_01.pde

P_1_2_3_01.pde

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
 * generates specific color palettes  
 * 
 * MOUSE
 * position x/y        : row and coloum count
 * 
 * KEYS
 * 0-9                 : creates specific color palettes
 * s                   : save png
 */

"""

class Sketch:
    def setup(self):
        self.size(800, 800)
        self.window_title("P_1_2_3_01")
        self.color_mode('HSB', 360, 100, 100)
        self.no_stroke()
        self.tile_count_x = 50
        self.tile_count_y = 10
        # arrays for color components values
        self.hue_values = [int(self.random(0, 360)) for _ in range(self.tile_count_x)]
        self.saturation_values = [int(self.random(0, 100)) for _ in range(self.tile_count_x)]
        self.brightness_values = [int(self.random(0, 100)) for _ in range(self.tile_count_x)]

    def draw(self):
        # white back
        self.background(0, 0, 100)

        # count every tile
        counter = 0

        # map mouse to grid resolution
        current_tile_count_x = int(self.map(self.mouse_x, 0, self.width, 1, self.tile_count_x))
        current_tile_count_y = int(self.map(self.mouse_y, 0, self.height, 1, self.tile_count_y))
        tile_width = self.width / float(current_tile_count_x)
        tile_height = self.height / float(current_tile_count_y)

        for grid_y in range(self.tile_count_y):
            for grid_x in range(self.tile_count_x):
                pos_x = tile_width * grid_x
                pos_y = tile_height * grid_y
                index = counter % current_tile_count_x

                # get component color values
                self.fill((self.hue_values[index], self.saturation_values[index], self.brightness_values[index]))
                self.rect(pos_x, pos_y, tile_width, tile_height)
                counter += 1

    def key_released(self):
        if self.key in ('s', 'S'):
            self.save_frame(f"P_1_2_3_01_##.png")

        if self.key == '1':
            for i in range(self.tile_count_x):
                self.hue_values[i] = int(self.random(0, 360))
                self.saturation_values[i] = int(self.random(0, 100))
                self.brightness_values[i] = int(self.random(0, 100))
        elif self.key == '2':
            for i in range(self.tile_count_x):
                self.hue_values[i] = int(self.random(0, 360))
                self.saturation_values[i] = int(self.random(0, 100))
                self.brightness_values[i] = 100
        elif self.key == '3':
            for i in range(self.tile_count_x):
                self.hue_values[i] = int(self.random(0, 360))
                self.saturation_values[i] = 100
                self.brightness_values[i] = int(self.random(0, 100))
        elif self.key == '4':
            for i in range(self.tile_count_x):
                self.hue_values[i] = 0
                self.saturation_values[i] = 0
                self.brightness_values[i] = int(self.random(0, 100))
        elif self.key == '5':
            for i in range(self.tile_count_x):
                self.hue_values[i] = 195
                self.saturation_values[i] = 100
                self.brightness_values[i] = int(self.random(0, 100))
        elif self.key == '6':
            for i in range(self.tile_count_x):
                self.hue_values[i] = 195
                self.saturation_values[i] = int(self.random(0, 100))
                self.brightness_values[i] = 100
        elif self.key == '7':
            for i in range(self.tile_count_x):
                self.hue_values[i] = int(self.random(0, 180))
                self.saturation_values[i] = int(self.random(80, 100))
                self.brightness_values[i] = int(self.random(50, 90))
        elif self.key == '8':
            for i in range(self.tile_count_x):
                self.hue_values[i] = int(self.random(180, 360))
                self.saturation_values[i] = int(self.random(80, 100))
                self.brightness_values[i] = int(self.random(50, 90))
        elif self.key == '9':
            for i in range(self.tile_count_x):
                if i % 2 == 0:
                    self.hue_values[i] = int(self.random(0, 360))
                    self.saturation_values[i] = 100
                    self.brightness_values[i] = int(self.random(0, 100))
                else:
                    self.hue_values[i] = 195
                    self.saturation_values[i] = int(self.random(0, 100))
                    self.brightness_values[i] = 100
        elif self.key == '0':
            for i in range(self.tile_count_x):
                if i % 2 == 0:
                    self.hue_values[i] = 192
                    self.saturation_values[i] = int(self.random(0, 100))
                    self.brightness_values[i] = int(self.random(10, 100))
                else:
                    self.hue_values[i] = 273
                    self.saturation_values[i] = int(self.random(0, 100))
                    self.brightness_values[i] = int(self.random(10, 90))
