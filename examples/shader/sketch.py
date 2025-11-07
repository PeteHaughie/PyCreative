"""
# Blur Filter
#
# Change the default shader to apply a simple, custom blur filter.
#
# Press the mouse to switch between the custom and default shader.
"""


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("Blur Filter Shader Example")
        self.blur = self.load_shader("blur.glsl")
        self.fill(255)
        self.pg = self.create_graphics(self.width, self.height)
        # Ensure the offscreen starts with a known background (avoid
        # sampling transparent pixels in the shader)
        self.pg.fill(255)
        self.pg.background(0)
        self.pg.stroke(255, 0, 0)
        self.pg.rect_mode("CENTER")
        self.pg.ellipse_mode("CENTER")
        self.background(0)

    def draw(self):
        # pass resolution as two floats
        self.blur.set("iResolution", float(self.width), float(self.height))
        # bind offscreen to sampler
        self.blur.set("iChannel0", self.pg)
    
        # render shapes to offscreen (clear it first so sampling isn't
        # reading transparent pixels)
        self.pg.begin_draw()
        self.pg.background(0)
        self.pg.square(self.mouse_x, self.mouse_y, 150)
        self.pg.circle(self.mouse_x, self.mouse_y, 100)
        self.pg.end_draw()
    
        # use shader and draw the offscreen texture
        self.shader(self.blur)
        self.image(self.pg, 0, 0, self.width, self.height)
        self.reset_shader()
