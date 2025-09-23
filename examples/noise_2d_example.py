from pycreative import Sketch
from pycreative.noise import PerlinNoise
from pycreative.pixels import Pixels


class Noise2DSketch(Sketch):
    def setup(self):
        self.size(400, 400, mode="cairo")
        self.noise = PerlinNoise(seed=42)
        self.pixels = Pixels(self.width, self.height)
        scale = 0.05  # Controls the "zoom" of the noise
        for x in range(self.width):
            for y in range(self.height):
                n = self.noise.noise2d(x * scale, y * scale)
                value = int(255 * n)
                value = max(0, min(255, value))  # Clamp to uint8 range
                self.pixels.set(x, y, (value, value, value))
        self.noise_surface = self.pixels.to_surface()

    def draw(self):
        # Use the Sketch API to draw the generated noise surface
        self.image(self.noise_surface, 0, 0)


if __name__ == "__main__":
    Noise2DSketch().run()
