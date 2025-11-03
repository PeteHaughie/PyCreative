"""
This is a recreation of the Generative Gestaltung example found at:
https://github.com/generative-design/Code-Package-Processing-3.x/blob/master/01_P/P_1_2_3_02/P_1_2_3_02.pde

P_1_2_3_02.pde

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
 * generates a specific color palette and some random "rect-tilings"
 *
 * MOUSE
 * left click          : new composition
 *
 * KEYS
 * s                   : save png
 */
"""


class Sketch:
    def setup(self):
        self.size(800, 800)
        self.window_title("P_1_2_3_02")
        self.color_mode("HSB", 360, 100, 100, 100)
        self.no_stroke()
        self.color_count = 20
        self.hue_values = [0] * self.color_count
        self.saturation_values = [0] * self.color_count
        self.brightness_values = [0] * self.color_count

    def draw(self):
        # ------ colors ------
        # create palette
        for i in range(self.color_count):
            if i % 2 == 0:
                self.hue_values[i] = int(self.random(0, 360))
                self.saturation_values[i] = 100
                self.brightness_values[i] = int(self.random(0, 100))
            else:
                self.hue_values[i] = 195
                self.saturation_values[i] = int(self.random(0, 100))
                self.brightness_values[i] = 100

        # ------ area tiling ------
        # count tiles
        counter = 0
        # row count and row height
        row_count = int(self.random(5, 40))
        row_height = float(self.height) / float(row_count)

        for i in range(row_count):
            # seperate each line in parts
            # how many fragments
            part_count = i + 1
            parts = []

            ii = 0
            while ii < part_count:
                # sub fragments or not?
                if self.random(1.0) < 0.075:
                    # take care of big values
                    fragments = int(self.random(2, 20))
                    part_count += fragments
                    for iii in range(fragments):
                        parts.append(self.random(2))
                else:
                    parts.append(self.random(2, 20))
                ii += 1

            # add all subparts
            sum_parts_total = sum(parts)

            # draw rects
            sum_parts_now = 0
            for part in parts:
                # get component color values
                index = counter % self.color_count
                self.fill(self.hue_values[index],
                           self.saturation_values[index],
                           self.brightness_values[index])

                sum_parts_now += part
                self.rect(self.map(sum_parts_now, 0, sum_parts_total, 0, self.width),
                          row_height * i,
                          self.map(part, 0, sum_parts_total,
                                   0, self.width) * -1,
                          row_height)
                counter += 1
        self.no_loop()

    def mouse_released(self):
        self.loop()
    
    def key_released(self):
        if self.key in ('s', 'S'):
            self.save_frame("P_1_2_3_02_##.png")
