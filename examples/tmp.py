class Sketch:

  def setup(self):
    self.size(800, 600)
    self.window_title("Temp Tests for PyCrteative Functionality")
    self.img = self.load_image('dont.png')
    self.img2 = self.img.copy()

  def draw(self):
    if self.img:
      self.image(self.img.resize(self.width, self.height), 0, 0)
      self.img2.tint(255, 0, 0, 128)
      self.image(self.img2.resize(self.width//2, self.height//2), 0, 0)

  def key_pressed(self):
    if self.key == 's':
      self.save_frame('tmp_output-####.png')