"""  /**
 * Noise2D 
 * by Daniel Shiffman.  
 * 
 * Using 2D noise to create simple texture. 
 */
 
float increment = 0.02;

void setup() {
  size(640, 360);
}

void draw() {
  
  loadPixels();

  float xoff = 0.0; // Start xoff at 0
  float detail = map(mouseX, 0, width, 0.1, 0.6);
  noiseDetail(8, detail);
  
  // For every x,y coordinate in a 2D space, calculate a noise value and produce a brightness value
  for (int x = 0; x < width; x++) {
    xoff += increment;   // Increment xoff 
    float yoff = 0.0;   // For every xoff, start yoff at 0
    for (int y = 0; y < height; y++) {
      yoff += increment; // Increment yoff
      
      // Calculate noise and scale by 255
      float bright = noise(xoff, yoff) * 255;

      // Try using this line instead
      //float bright = random(0,255);
      
      // Set each pixel onscreen to a grayscale value
      pixels[x+y*width] = color(bright);
    }
  }
  
  updatePixels();
}
"""
class Sketch:
    """Draw a 2D noise field to the canvas.

    This sketch demonstrates using the built-in `noise()` function to
    create a procedurally generated noise texture. No external libraries
    are required.
    """

    def setup(self):
        self.size(640, 360)
        self.window_title('Noise2D demo')
        # Pre-generate a static noise image so the field does not change
        # each frame. This mirrors many Processing examples where the noise
        # texture is computed once and displayed.
        # smaller step -> smoother transitions; reduce to 0.005 for smoother output
        self._noise_increment = 0.005
        self._noise_octaves = 4
        self._noise_falloff = 0.5
        try:
            self.noise_detail(self._noise_octaves, self._noise_falloff)
        except Exception:
            pass
        # seed the noise for reproducible, static output across runs
        try:
            self.noise_seed(0)
        except Exception:
            pass
        # create an image buffer we will update each frame (keeps interactivity)
        try:
            self.img = self.create_image(self.width, self.height)
        except Exception:
            self.img = None

        # normal setup: image created above; no debug snapshots by default

    def draw(self):
        # Recompute the noise field each frame to preserve interactivity
        # with `mouse_x` controlling noise_detail.
        if getattr(self, 'img', None) is None:
            return
        # Compute a full noise field using the vectorized helper. This is
        # much faster than calling `noise()` per-pixel from Python.
        try:
            mx = getattr(self, 'mouse_x', 0)
            detail = self.map(mx, 0, self.width, 0.1, 0.6)
            self.noise_detail(8, detail)
        except Exception:
            detail = None

        inc = 0.02
        try:
            arr = self.noise_field(self.width, self.height, x0=0.0, y0=0.0, inc=inc)
            # If a numpy array was returned, write it into the PCImage in one call
            if arr is not None:
                try:
                    self.img.set_from_array(arr)
                except Exception:
                    # fallback: if set_from_array missing, convert to bytes
                    try:
                        h, w = arr.shape
                        # create RGBA bytes from grayscale
                        import numpy as _np

                        rgba = _np.empty((h, w, 4), dtype=_np.uint8)
                        rgba[:, :, 0] = arr
                        rgba[:, :, 1] = arr
                        rgba[:, :, 2] = arr
                        rgba[:, :, 3] = 255
                        self.img.set_bytes(0, 0, w, h, rgba.tobytes(), mode='RGBA')
                    except Exception:
                        pass
            else:
                # If vectorized helper unavailable, gracefully fall back to per-pixel
                # sampling (slower path preserved for compatibility).
                inc = 0.02
                xoff = 0.0
                for x in range(self.width):
                    xoff += inc
                    yoff = 0.0
                    for y in range(self.height):
                        yoff += inc
                        try:
                            n = float(self.noise(xoff, yoff))
                            bright = int(max(0, min(255, round(n * 255))))
                        except Exception:
                            bright = int(max(0, min(255, round(self.random(0, 255)))))
                        try:
                            self.img.set(x, y, (bright, bright, bright, 255))
                        except Exception:
                            continue
        except Exception:
            # If anything fails, fall back to the original per-pixel method
            try:
                inc = 0.02
                xoff = 0.0
                for x in range(self.width):
                    xoff += inc
                    yoff = 0.0
                    for y in range(self.height):
                        yoff += inc
                        try:
                            n = float(self.noise(xoff, yoff))
                            bright = int(max(0, min(255, round(n * 255))))
                        except Exception:
                            bright = int(max(0, min(255, round(self.random(0, 255)))))
                        try:
                            self.img.set(x, y, (bright, bright, bright, 255))
                        except Exception:
                            continue
            except Exception:
                pass

        try:
            self.img.update_pixels()
        except Exception:
            pass
        # normal draw: do not write debug snapshots here

        try:
            self.image(self.img, 0, 0)
        except Exception:
            pass

    def key_pressed(self):
        # Press 'r' to regenerate the noise image (reseeds internally)
        if getattr(self, 'key', None) == 'r':
            try:
                self._generate_noise_image()
            except Exception:
                pass

    def _generate_noise_image(self):
        # Helper to (re)populate self.img with noise values
        if getattr(self, 'img', None) is None:
            return
        # Use the vectorized noise_field when possible for regeneration
        inc = getattr(self, '_noise_increment', 0.01)
        try:
            arr = self.noise_field(self.width, self.height, x0=0.0, y0=0.0, inc=inc)
            if arr is not None:
                try:
                    self.img.set_from_array(arr)
                except Exception:
                    # fallback to bytes
                    try:
                        import numpy as _np

                        h, w = arr.shape
                        rgba = _np.empty((h, w, 4), dtype=_np.uint8)
                        rgba[:, :, 0] = arr
                        rgba[:, :, 1] = arr
                        rgba[:, :, 2] = arr
                        rgba[:, :, 3] = 255
                        self.img.set_bytes(0, 0, w, h, rgba.tobytes(), mode='RGBA')
                    except Exception:
                        pass
                return
        except Exception:
            pass

        # Fallback: per-pixel sampling
        try:
            xoff = 0.0
            for x in range(self.width):
                xoff += inc
                yoff = 0.0
                for y in range(self.height):
                    yoff += inc
                    try:
                        n = float(self.noise(xoff, yoff))
                        bright = int(max(0, min(255, round(n * 255))))
                    except Exception:
                        bright = int(max(0, min(255, round(self.random(0, 255)))))
                    try:
                        self.img.set(x, y, (bright, bright, bright, 255))
                    except Exception:
                        continue
        except Exception:
            pass
        try:
            self.img.update_pixels()
        except Exception:
            pass
