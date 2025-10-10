"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_14_COS_SIN_LUT/Example_5_14_COS_SIN_LUT.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Using a Lookup Table for Sine and Cosine
"""

from pycreative.app import Sketch


class Example_5_14_COS_SIN_LUT(Sketch):
    def settings(self):
        self.size(640, 360)

    def setup(self):
        self.initSinCos()  # important call to initialize lookup tables

    def draw(self):
        self.background(255)
        # modulate the current radius
        radius = 50 + 50 * self.sinLUT[self.frame_count % self.SC_PERIOD]

        # draw a circle made of points (every 5 degrees)
        for i in range(0, 360, 5):
            # convert degrees into array index:
            # the modulo operator (%) ensures periodicity
            theta = int((i * self.SC_INV_PREC) % self.SC_PERIOD)
            self.stroke(0)
            self.stroke_weight(4)
            # draw the circle around mouse pos
            self.point(
                self.width / 2 + radius * self.cosLUT[theta],
                self.height / 2 + radius * self.sinLUT[theta],
            )

    # declare arrays and params for storing sin/cos values
    sinLUT = []
    cosLUT = []
    # set table precision to 0.5 degrees
    SC_PRECISION = 0.5
    # caculate reciprocal for conversions
    SC_INV_PREC = 1 / SC_PRECISION
    # compute required table length
    SC_PERIOD = int(360 * SC_INV_PREC)

    # init sin/cos tables with values
    # should be called from setup()
    def initSinCos(self):
        # initialize as floats so type checkers infer List[float]
        self.sinLUT = [0.0] * self.SC_PERIOD
        self.cosLUT = [0.0] * self.SC_PERIOD
        for i in range(self.SC_PERIOD):
            self.sinLUT[i] = self.sin(i * (self.PI / 180) * self.SC_PRECISION)
            self.cosLUT[i] = self.cos(i * (self.PI / 180) * self.SC_PRECISION)
