"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_4_Flow_Field/Example_5_4_Flow_Field.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Flow Field Following
// Via Reynolds: http://www.red3d.com/cwr/steer/FlowFollow.html
"""

from pycreative.app import Sketch
from FlowField import FlowField
from Vehicle import Vehicle


class Example_5_04_Flow_Field(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title('Example 5.4: Flow Field Following')
        print("Hit space bar to toggle debugging lines.\nClick the mouse to generate a new flow field.")
        # Make a new flow field with "resolution" of 16
        self.flowfield = FlowField(self, 20)
        self.vehicles = []
        # Make a whole bunch of vehicles with random maxspeed and maxforce values
        import random
        for _ in range(120):
            ms = random.uniform(2, 5)
            mf = random.uniform(0.1, 0.5)
            v = Vehicle(self, random.uniform(0, self.width), random.uniform(0, self.height), ms, mf)
            self.vehicles.append(v)
        self.debug = True

    def update(self, dt):
        pass

    def draw(self):
        self.clear((255, 255, 255))
        # Display the flowfield in "debug" mode
        self.flowfield.show(self.debug)
        # Tell all the vehicles to follow the flow field
        for v in self.vehicles:
            v.follow(self.flowfield)
            v.run()

    def key_pressed(self):
        if self.key == 'space':
            self.debug = not self.debug

    def mouse_pressed(self):
        # Make a new flowfield
        self.flowfield.init()
