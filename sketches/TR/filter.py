"""
Floyd–Steinberg dithering for an OffscreenSurface.

This implementation prefers the `pg.pixels()` context manager which may
provide a NumPy-backed PixelView for faster manipulation. If unavailable it
falls back to per-pixel get/set operations on the surface.


// Original Processing code by Tim Rodenbroeker:
void applyFloydSteinbergDither(PGraphics pg) {
  pg.loadPixels();

  int w = pg.width;
  int h = pg.height;

  for (int y = 0; y < h; y++) {
    for (int x = 0; x < w; x++) {
      // Get the current pixel color
      color oldColor = pg.pixels[y * w + x];

      // Convert to grayscale (you can skip this step if you want to dither in color)
      float gray = brightness(oldColor);

      // Find the nearest color (0 or 255 in grayscale)
      int newColor = gray < 128 ? color(0) : color(255);
      pg.pixels[y * w + x] = newColor;

      // Calculate the quantization error
      float error = gray - brightness(newColor);

      // Distribute the error to the neighboring pixels
if (x + 1 < w) pg.pixels[y * w + (x + 1)] = adjustBrightness(pg.pixels[y * w + (x + 1)], error * 7 / 16);
if (x - 1 >= 0 && y + 1 < h) pg.pixels[(y + 1) * w + (x - 1)] = adjustBrightness(pg.pixels[(y + 1) * w + (x - 1)], error * 3 / 16);
if (y + 1 < h) pg.pixels[(y + 1) * w + x] = adjustBrightness(pg.pixels[(y + 1) * w + x], error * 5 / 16);
if (x + 1 < w && y + 1 < h) pg.pixels[(y + 1) * w + (x + 1)] = adjustBrightness(pg.pixels[(y + 1) * w + (x + 1)], error * 1 / 16);    }
  }

  pg.updatePixels();
}

color adjustBrightness(color c, float adjustment) {
  float newBrightness = brightness(c) + adjustment;
  newBrightness = constrain(newBrightness, 0, 255);
  return color(newBrightness);
}
"""


def _lum(r: int, g: int, b: int) -> int:
    # simple luminance to grayscale 0-255
    return int(0.2126 * r + 0.7152 * g + 0.0722 * b)


def apply_floyd_steinberg_dither(pg) -> None:
    """Apply in-place Floyd–Steinberg dithering to `pg`.

    Args:
        pg: OffscreenSurface-like object exposing `pixels()` context manager or
            `get(x,y)`/`set(x,y,color)` methods and `size` attribute.
    """
    w, h = pg.size

    # Try PixelView path
    try:
        with pg.pixels() as pv:
            # pv may be numpy-backed with shape (h,w,3) or a list-like buffer.
            # Several PixelView implementations provide a `raw()` method exposing
            # the underlying data; prefer numpy if available.
            raw = getattr(pv, "raw", None)
            arr = None
            if raw is not None:
                data = raw()
                # numpy arrays have 'astype' method
                if hasattr(data, "astype"):
                    arr = data
            if arr is not None:
                # Convert to float to accumulate errors
                f = arr.astype('float32')
                for y in range(h):
                    for x in range(w):
                        old = f[y, x, :3]
                        gray = _lum(int(old[0]), int(old[1]), int(old[2]))
                        new_val = 255 if gray > 127 else 0
                        err = gray - new_val
                        f[y, x, 0:3] = new_val
                        # distribute error
                        if x + 1 < w:
                            f[y, x + 1, 0:3] += err * 7 / 16
                        if x - 1 >= 0 and y + 1 < h:
                            f[y + 1, x - 1, 0:3] += err * 3 / 16
                        if y + 1 < h:
                            f[y + 1, x, 0:3] += err * 5 / 16
                        if x + 1 < w and y + 1 < h:
                            f[y + 1, x + 1, 0:3] += err * 1 / 16
                # clamp and write back
                f = f.clip(0, 255).astype('uint8')
                # some PixelView implementations offer set_from_numpy
                if hasattr(pv, "set_from_numpy"):
                    pv.set_from_numpy(f)
                else:
                    # write back per-pixel
                    for y in range(h):
                        for x in range(w):
                            v = tuple(int(vv) for vv in f[y, x, :3])
                            pv[y, x] = v
                return

            # else fall back to PixelView API access
            for y in range(h):
                for x in range(w):
                    px = pv[y, x]
                    r, g, b = px[0], px[1], px[2]
                    gray = _lum(r, g, b)
                    new_val = 255 if gray > 127 else 0
                    pv[y, x] = (new_val, new_val, new_val)
                    err = gray - new_val
                    if x + 1 < w:
                        rr, gg, bb = pv[y, x + 1][0:3]
                        gval = _lum(rr, gg, bb) + err * 7 / 16
                        v = int(max(0, min(255, gval)))
                        pv[y, x + 1] = (v, v, v)
                    if x - 1 >= 0 and y + 1 < h:
                        rr, gg, bb = pv[y + 1, x - 1][0:3]
                        gval = _lum(rr, gg, bb) + err * 3 / 16
                        v = int(max(0, min(255, gval)))
                        pv[y + 1, x - 1] = (v, v, v)
                    if y + 1 < h:
                        rr, gg, bb = pv[y + 1, x][0:3]
                        gval = _lum(rr, gg, bb) + err * 5 / 16
                        v = int(max(0, min(255, gval)))
                        pv[y + 1, x] = (v, v, v)
                    if x + 1 < w and y + 1 < h:
                        rr, gg, bb = pv[y + 1, x + 1][0:3]
                        gval = _lum(rr, gg, bb) + err * 1 / 16
                        v = int(max(0, min(255, gval)))
                        pv[y + 1, x + 1] = (v, v, v)
            return
    except Exception:
        # If pixels() isn't supported or something else failed, fall back
        # to per-pixel get/set on the surface.
        pass

    # Fallback: per-pixel get/set on the surface
    for y in range(h):
        for x in range(w):
            col = pg.get(x, y)
            try:
                r, g, b = col[0], col[1], col[2]
            except Exception:
                r = (col >> 16) & 255
                g = (col >> 8) & 255
                b = col & 255

            gray = _lum(r, g, b)
            new_val = 255 if gray > 127 else 0
            pg.set(x, y, (new_val, new_val, new_val))
            err = gray - new_val
            if x + 1 < w:
                rr, gg, bb = pg.get(x + 1, y)[0:3]
                gval = _lum(rr, gg, bb) + err * 7 / 16
                pg.set(x + 1, y, (int(max(0, min(255, gval))),) * 3)
            if x - 1 >= 0 and y + 1 < h:
                rr, gg, bb = pg.get(x - 1, y + 1)[0:3]
                gval = _lum(rr, gg, bb) + err * 3 / 16
                pg.set(x - 1, y + 1, (int(max(0, min(255, gval))),) * 3)
            if y + 1 < h:
                rr, gg, bb = pg.get(x, y + 1)[0:3]
                gval = _lum(rr, gg, bb) + err * 5 / 16
                pg.set(x, y + 1, (int(max(0, min(255, gval))),) * 3)
            if x + 1 < w and y + 1 < h:
                rr, gg, bb = pg.get(x + 1, y + 1)[0:3]
                gval = _lum(rr, gg, bb) + err * 1 / 16
                pg.set(x + 1, y + 1, (int(max(0, min(255, gval))),) * 3)