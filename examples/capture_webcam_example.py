from pycreative import Sketch
from pycreative.capture import Capture

class WebcamSketch(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Webcam Capture Example")
        self.cam = Capture(0)
        self.cam.start()
        self.bg = (30, 30, 30)

    def draw(self):
        self.clear(self.bg)
        frame = self.cam.get_frame()
        if frame:
            self.image(frame, 0, 0, self.width, self.height)
        else:
            self.text("No webcam frame available", self.width//2, self.height//2, center=True, color=(200,50,50), size=32)

    def teardown(self):
        self.cam.stop()

if __name__ == "__main__":
    WebcamSketch().run()
