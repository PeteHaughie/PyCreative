"""draw_pg(sketch)

Converted Processing sketch: draws a grid of small rotating rectangles into
an offscreen `pg` buffer, then applies a Floyd–Steinberg dithering pass.

This function expects to be called as `draw_pg(self)` from a `Sketch` where
`self.pg` is an `OffscreenSurface` (created with
`self.create_graphics(w,h)`).

// Original Processing code by Tim Rodenbroeker:

void drawPg() {

  float driver = map(frameCount, 0, dur, 0, 360);

  pg.beginDraw();
  float b = map(sin(radians(driver)), -1, 1, 0, 255);
  pg.background(b);

  float mag = pg.width * 0.9;
  float step = 360 / float(elements);

  pg.noStroke();
  pg.rectMode(CENTER);
  pg.fill(0);

  for (int j = 0; j < elements; j++) {
    for (int i = 0; i < elements; i++) {

      float mag2 = map(sin(radians(driver + j * i)), -1, 1, mag, mag);
      float stepOutside = mag2 / float(elements);
      //int px = int(sin(radians(i))* mag);
      //int py = int(cos(radians(j))* mag2);

      float wave = sin(radians(driver + j * i * 0.01)) * 55;

      float e = map(sin(radians(driver * 2 + i * 8 + j * 8)), -1, 1, 0, 255);
      pg.fill(e);
      int x = int(sin(radians(i*step * 8))* j * stepOutside);
      int y = int(cos(radians(j*step*1 + driver * 1))* j * stepOutside);
      pg.push();
      pg.translate(pg.width/2 + wave + x, pg.height/2+y);
      pg.rotate(radians(driver + j));
      pg.rect(0, 0, 5, 32);

      pg.pop();
    }
  }

  pg.endDraw();
  applyFloydSteinbergDither(pg);
  // pg.filter(GRAY);
  // pg.filter(POSTERIZE, 3);
  // pg.filter(INVERT);
}

"""

import math
# from filter import apply_floyd_steinberg_dither

# parameters from the original sketch
elements = 64
dur = 100


def _map(v, a, b, c, d):
    # linear map v from range [a,b] to [c,d]
    return c + (d - c) * ((v - a) / (b - a)) if b != a else c


def draw_pg(sketch):
    """Render into `sketch.pg` (an OffscreenSurface)."""
    if not hasattr(sketch, "pg") or sketch.pg is None:
        return

    pg = sketch.pg
    # driver maps frame_count -> 0..360 over dur frames
    driver = _map(sketch.frame_count % dur, 0, dur, 0, 360)

    # Draw into the offscreen buffer each frame
    with pg:
        # background pulses with a sin() driver
        b = _map(math.sin(math.radians(driver)), -1, 1, 0, 255)
        pg.clear((int(b), int(b), int(b)))

        mag = pg.size[0] * 0.9
        step = 360.0 / float(elements)

        pg.no_stroke()
        pg.rect_mode(pg.MODE_CENTER)
        # iterate grid and draw small rectangles using local transforms
        for j in range(elements):
            for i in range(elements):
                # wave / offset
                mag2 = mag
                step_outside = mag2 / float(elements)
                wave = math.sin(math.radians(driver + j * i * 0.01)) * 55

                e = int(_map(math.sin(math.radians(driver * 2 + i * 8 + j * 8)), -1, 1, 0, 255))
                pg.fill((e, e, e))

                x = int(math.sin(math.radians(i * step * 8)) * j * step_outside)
                y = int(math.cos(math.radians(j * step * 1 + driver * 1)) * j * step_outside)

                with pg.transform(translate=(pg.size[0] / 2 + wave + x, pg.size[1] / 2 + y), rotate=math.radians(driver + j)):
                    pg.rect(0, 0, 5, 32)

    # apply dithering to the offscreen surface
    # try:
    #     apply_floyd_steinberg_dither(pg)
    # except Exception:
    #     # non-fatal: don't crash the sketch if dithering fails
    #     pass
