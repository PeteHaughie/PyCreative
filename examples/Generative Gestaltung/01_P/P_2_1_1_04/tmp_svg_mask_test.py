class Sketch:
    def setup(self):
        self.size(200, 200)
        self.background(255)
        self.s = self.load_shape('module_1.svg')

    def draw(self):
        self.background(255)
        # disable SVG internal style and set semi-transparent fill
        self.s.disable_style()
        self.fill(0, 130, 164, 128)
        self.no_stroke()
        # draw at center scaled to half size of canvas
        self.push_matrix()
        self.translate(self.width/2, self.height/2)
        self.shape_mode('CENTER')
        self.shape(self.s, 0, 0, 150, 150)
        self.pop_matrix()
