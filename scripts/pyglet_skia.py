import skia
import pyglet


width, height = 800, 600
window = pyglet.window.Window(width, height, "Skia-Pyglet")
# Create a Skia surface that matches the window size
surface = skia.Surface(width, height)

with surface as canvas:
  paint = skia.Paint(
      Color=skia.ColorBLUE,
      Style=skia.Paint.kFill_Style,
      AntiAlias=True
  )
  canvas.drawRect(skia.Rect(100, 100, 300, 300), paint)

image = surface.makeImageSnapshot()
# Convert Skia image to a format pyglet can use
data = image.tobytes()
img = pyglet.image.ImageData(width, height, 'RGBA', data, pitch=-width * 4)

@window.event
def on_draw():
  img.blit(0, 0)

pyglet.app.run()