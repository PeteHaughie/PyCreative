# Offscreen Surfaces (PGraphics-like)

Offscreen surfaces let you draw into a Surface buffer that is not the main window. This is useful for caching expensive static content, preparing layered composition, or rendering at different resolutions.

Key APIs

- `Sketch.create_graphics(width, height) -> OffscreenSurface`
  - Returns an `OffscreenSurface` that mirrors the `Surface` API used by the main sketch canvas.
  - The returned object exposes `.raw` (the underlying `pygame.Surface`) for low-level operations.

- `OffscreenSurface` methods (most `Surface` methods are available):
  - `fill(color)`, `stroke(color)`, `stroke_weight(w)`, `rect(...)`, `ellipse(...)`, `polyline(...)`, `polygon(...)`, `arc(...)`, `text(...)`, `load_image(path)`, etc.
  - `blit_image(img, x, y)` — convenience to blit a `pygame.Surface` or an OffscreenSurface-like object directly.
  - `save(path)` — best-effort save using `pygame.image.save()`.
  - Context manager support: `with off:` allows explicit scoping for convenience.
  - `raw` property: the underlying `pygame.Surface` (useful for direct blits or interop).

Examples

Simple caching pattern:

```py
# inside a Sketch
if self._cache is None:
    off = self.create_graphics(300, 200)
    with off:
        # Offscreen surfaces, caching, and no_loop

        This short guide explains common idioms for rendering static or expensive content into an offscreen buffer and composing it into your main sketch.

        ## Key concepts

        - `create_graphics(w, h, inherit_state=False)` — create an `OffscreenSurface` that mirrors the main `Surface` API. Use `inherit_state=True` to copy drawing state (fill/stroke/weights) from the current main surface.

        - `cached_graphics(key, w, h, render_fn)` — create and cache an `OffscreenSurface` produced by `render_fn`. Handy when you want the system to manage caching for you.

        - `no_loop(key, w, h, render_fn)` — backward-compatible alias for `cached_graphics` (keeps old examples working).

        - `no_loop()` (no args) — runtime control: when called from `setup()` the runtime will call `draw()` once and then suppress further draws until `loop()` is called.

        - `image(img, x, y, w=None, h=None)` — draw an image or `OffscreenSurface` into the current surface, optionally scaling to `w` x `h`.

        ## When to render in `setup()` vs `draw()`

        - If your offscreen content is static (e.g., a texture, background pattern, or complex precomputation) render it once in `setup()` into an `OffscreenSurface` and reuse it in `draw()`.

        - If you need the framework to manage caching for you, use `cached_graphics()` (or `no_loop(key, ...)` for backward compatibility). This is convenient for examples where you want a lexical cache keyed by a string.

        - Use `no_loop()` (runtime, no args) when you want your sketch to render once and then pause (helpful for export scripts or static renders).

        ## Example: pre-render in setup (preferred)

        ```py
        class MySketch(Sketch):
          def setup(self):
            self.size(800, 600)
            self.no_loop()  # draw() will run once then pause
            self.off = self.create_graphics(400, 300, inherit_state=True)
            with self.off:
              self.off.clear((0,0,0))
              # expensive rendering here

          def draw(self):
            self.clear((240,240,240))
            self.image(self.off, 100, 100)
        ```

        ## Example: cached_graphics (convenient)

        ```py
        class SketchCached(Sketch):
          def draw(self):
            self.clear((255,255,255))
            off = self.cached_graphics("pattern", 300, 200, lambda pg: draw_pattern(pg))
            self.image(off, 50, 50)
        ```

        ## Notes and compatibility

        - `no_loop(key, ...)` remains as an alias for `cached_graphics(key, ...)` to keep older examples working.
        - Prefer `image()` in new code; `blit_image()` is still present for backward compatibility but delegates to `image()`.
        - Offscreen surfaces expose the same drawing API as the main surface (rect, ellipse, polyline, etc.) and are context-manager friendly (`with off:`) so code can reuse drawing logic between on-screen and offscreen targets.

        If you'd like, I can expand this page with diagrams, an additional example showing scaling, and a unit test that asserts `no_loop()` runtime behavior.
