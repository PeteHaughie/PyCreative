# Offscreen Surfaces (PGraphics-like)

Offscreen surfaces let you draw into a Surface buffer that is not the main window. This is useful for caching expensive static content, preparing layered composition, or rendering at different resolutions.

Key APIs

- `Sketch.create_graphics(width, height, inherit_state=False) -> OffscreenSurface`
  - Returns an `OffscreenSurface` that mirrors the `Surface` API used by the main sketch canvas.
  - When `inherit_state=True` the OffscreenSurface copies the current drawing state (fill, stroke, stroke_weight, caps/joins) so drawn content matches the main surface when convenient.

- `OffscreenSurface` (most `Surface` methods are available):
  - `fill(color)`, `stroke(color)`, `stroke_weight(w)`, `rect(...)`, `ellipse(...)`, `polyline(...)`, `polygon(...)`, `arc(...)`, `text(...)`, `load_image(path)`, etc.
  - `blit_image(img, x, y)` — convenience to blit a `pygame.Surface` or an OffscreenSurface-like object directly.
  - `save(path)` — best-effort save using `pygame.image.save()`.
  - Context manager support: `with off:` temporarily sets the offscreen buffer as the active drawing target for the duration of the block.
  - `raw` property: the underlying `pygame.Surface` (useful for direct blits or interop).

Examples and patterns

Simple pre-render into an offscreen buffer and reuse each frame:

```py
class MySketch(Sketch):
    def setup(self):
        self.size(800, 600)
        # prepare an offscreen buffer that inherits current style
        self.off = self.create_graphics(400, 300, inherit_state=True)
        with self.off:
            self.clear((0,0,0))
            self.fill((255,128,0))
            self.ellipse(200,150,180,120)

    def draw(self):
        self.clear((240,240,240))
        # blit the pre-rendered buffer to the main surface
        self.image(self.off, 100, 50)

if __name__ == '__main__':
    MySketch().run()
```

Cached graphics helper

Use `cached_graphics(key, w, h, render_fn)` to create and reuse an `OffscreenSurface` for repeated draws. This is handy for content keyed by a small string (e.g., a tileset or generated pattern).

```py
def draw_pattern(pg: OffscreenSurface):
    with pg:
        pg.clear((0,0,0))
        pg.fill((40,100,200))
        pg.rect(10,10,100,100)

class SketchCached(Sketch):
    def draw(self):
        self.clear((255,255,255))
        off = self.cached_graphics('pattern', 300, 200, draw_pattern)
        self.image(off, 50, 50)
```

When to render in `setup()` vs `draw()`

- If your offscreen content is static (texture, background pattern, or complex precomputation) render it once in `setup()` into an `OffscreenSurface` and reuse it in `draw()`.
- If you need automatic caching, use `cached_graphics()`; it manages creation and reuse for keyed content.

Notes and compatibility

- Prefer `image()` in new code; `blit_image()` remains for backward compatibility but delegates to `image()`.
- Offscreen surfaces expose the same drawing API as the main surface and are context-manager friendly (`with off:`) so code can reuse drawing logic between on-screen and offscreen targets.
- When saving images, `OffscreenSurface.save(path)` is a convenience that delegates to Pygame's image save; for more control use the `raw` property and your own image library.

If you'd like, I can add diagrams, a scaling example, or an integration test demonstrating offscreen rendering and pixel assertions.
          def draw(self):

## Per-frame offscreen rendering (idiomatic pattern)

There are two common patterns when using offscreen surfaces:

- Static pre-render (render once in `setup()` and blit each frame) — good for
    expensive, unchanging content.
- Per-frame offscreen (render into the offscreen buffer every frame, then
    blit) — idiomatic when the offscreen content itself is animated or when you
    want the offscreen buffer to manage its own local transforms/state.

Per-frame offscreen is often simpler and more explicit: sketches redraw the
offscreen content each frame (`with off:` inside `draw()`), apply local
transforms with `off.transform(...)`, then blit the resulting buffer to the
main surface with `image(off, x, y, w, h)`.

If you want an offscreen buffer to inherit the main surface's transform at
creation time use `create_graphics(..., inherit_transform=True)`. This copies
the current transform matrix onto the new offscreen surface. If you need the
offscreen to stay in sync with ongoing changes to the main matrix you must
copy the matrix each frame (e.g., `off.set_matrix(self.surface.get_matrix())`) before
rendering into `off`.
