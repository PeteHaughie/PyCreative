"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/P_1_2_2_01/P_1_2_2_01.pde

P_1_2_2_01.pde

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
 * extract and sort the color palette of an image
 * 	 
 * MOUSE
 * position x          : resolution
 * 
 * KEYS
 * 1-3                 : load different images
 * 4                   : no color sorting
 * 5                   : sort colors on hue
 * 6                   : sort colors on saturation
 * 7                   : sort colors on brightness
 * 8                   : sort colors on grayscale (luminance)
 * s                   : save png
 */
"""


class Sketch:
    def setup(self):
        self.size(600, 600)
        self.set_title("P_1_2_2_01")
        self.color_mode('HSB', 360, 100, 100)
        self.no_stroke()
        # self.no_cursor()
        self.img = self.load_image("pic1.jpg")
        self.colors = []
        self.sort_mode = None

    def draw(self):
        self.background(0)
        tile_count = self.width // max(self.mouse_x, 5)
        rect_size = int(self.width / float(tile_count))

        # get colors from image
        self.colors = []
        for grid_y in range(tile_count):
            for grid_x in range(tile_count):
                px = int(grid_x * rect_size)
                py = int(grid_y * rect_size)
                col = self.img.get(px, py)
                self.colors.append(col)

        # sort colors
        if self.sort_mode is not None:
            self.colors = self.sort_colors(self.colors, self.sort_mode)

        # draw grid
        i = 0
        for grid_y in range(tile_count):
            for grid_x in range(tile_count):
                self.fill(self.colors[i])
                self.rect(grid_x * rect_size, grid_y * rect_size, rect_size, rect_size)
                i += 1

    def sort_colors(self, colors, mode):
        if mode == 'HUE':
            return sorted(colors, key=lambda c: self.hue(c))
        elif mode == 'SATURATION':
            return sorted(colors, key=lambda c: self.saturation(c))
        elif mode == 'BRIGHTNESS':
            return sorted(colors, key=lambda c: self.brightness(c))
        elif mode == 'GRAYSCALE':
            return sorted(colors, key=lambda c: self.red(c) * 0.299 + self.green(c) * 0.587 + self.blue(c) * 0.114)
        else:
            return colors

    def key_released(self):
        if self.key in ['s', 'S']:
            self.save_frame("P_1_2_2_01_##.png")

        if self.key == '1':
            self.img = self.load_image("pic1.jpg")
        elif self.key == '2':
            self.img = self.load_image("pic2.jpg")
        elif self.key == '3':
            self.img = self.load_image("pic3.jpg")
        elif self.key == '4':
            self.sort_mode = None
        elif self.key == '5':
            self.sort_mode = 'HUE'
        elif self.key == '6':
            self.sort_mode = 'SATURATION'
        elif self.key == '7':
            self.sort_mode = 'BRIGHTNESS'
        elif self.key == '8':
            self.sort_mode = 'GRAYSCALE'
