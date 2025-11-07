"""
Hello World — visible example

This is a minimal, guaranteed-to-work sketch that fills the canvas with
magenta using the standard drawing APIs. It's intentionally simple so you
can confirm the rendering pipeline is functioning before we reintroduce
shader/GL experiments.
"""

class Sketch:
    def setup(self):
        self.size(320, 240)
        # load a fragment shader file named 'tint.frag' in the same folder or data/
        shader = load_shader('ting.vert', 'tint.frag')  # returns a PCShader or None
        if shader:
            self.shader(shader)
    
    def draw(self):
        self.no_stroke()
        # draw a rect that will be shaded by the active shader
        self.rect(0, 0, self.width, self.height)
