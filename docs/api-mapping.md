# API Mapping: Processing / openFrameworks -> PyCreative

This document maps common concepts and APIs from Processing and openFrameworks to the PyCreative API surface. It exists to help users familiar with those frameworks migrate quickly and for implementers to preserve expected ergonomics.

Conventions
- PyCreative `Sketch` is the primary entrypoint, similar to Processing sketches and openFrameworks `ofBaseApp` implementations.
- Coordinate system: origin (0,0) is top-left, x increases to the right, y increases downward (pixels).
- Immediate-mode drawing: shapes are drawn each frame within `draw()`; state (fill/stroke) is managed per-call or via simple helpers.

Mapping
 - Processing `setup()` -> PyCreative `Sketch.setup(self)` — Done
 - Processing `draw()` -> PyCreative `Sketch.draw(self)` — Done
 - Processing `size(w, h)` -> PyCreative `self.size(w, h, fullscreen=False)` — Done
 - Processing `frameRate(fps)` -> PyCreative `self.frame_rate(fps)` — Done
 - Processing `ellipse(x, y, w, h)` -> PyCreative `self.ellipse(x, y, w, h, fill=None, stroke=None)` — Done
 - Processing `rect(x, y, w, h)` -> PyCreative `self.rect(x, y, w, h, fill=None, stroke=None)` — Done
 - Processing `line(x1, y1, x2, y2)` -> PyCreative `self.line(x1, y1, x2, y2, stroke=None)` — Done
 - Processing `keyPressed()` / `mousePressed()` -> PyCreative `Sketch.on_event(self, event)` with unified `InputEvent` objects — Done
 - openFrameworks `ofBaseApp::setup/update/draw` -> PyCreative `Sketch.setup/update/draw` — Done

Migration notes for implementers
- Keep method names and behavior ergonomic for Python (snake_case), but maintain semantic parity with Processing/openFrameworks where practical.
- Provide discoverability: helper methods for common actions (e.g., `set_title()`, `frame_rate()`) and clear docstrings.
- Document any deviations and the rationale in `docs/api-mapping.md`.

Examples
- `examples/example_sketch.py` demonstrates `setup`, `update(dt)`, `draw`, `size()`, and basic primitives.
- `examples/input_example.py` demonstrates `on_event(event)` usage.

Non-normative
- This mapping is for ergonomics and learning; it does not permit copying or referencing proprietary source from Processing/openFrameworks.

## Expanded Processing API Coverage

The following expands the mapping to cover the most commonly used Processing APIs. The goal is to provide a pragmatic, testable subset that supports the majority of beginner and intermediate sketches.

Note: The left column is the canonical Processing name; the right column shows the suggested PyCreative equivalent (snake_case) and short notes about behavior or differences.

Graphics primitives & drawing
 - ellipse(x, y, w, h) -> self.ellipse(x, y, w, h, fill=None, stroke=None) — Done
 - rect(x, y, w, h) -> self.rect(x, y, w, h, fill=None, stroke=None) — Done
 - line(x1, y1, x2, y2) -> self.line(x1, y1, x2, y2, stroke=None) — Done
 - triangle(x1,y1, x2,y2, x3,y3) -> self.triangle(...) — Done
 - quad(x1,y1, x2,y2, x3,y3, x4,y4) -> self.quad(...) — Done
 - point(x, y) -> self.point(x, y) — Done

Shape construction
 - beginShape()/vertex()/endShape(CLOSE) -> self.begin_shape(); self.vertex(...); self.end_shape(close=True/False) — Todo
 - bezier(), bezierVertex(), curve(), curveVertex() -> self.bezier(...), self.curve(...) — Todo

Drawing state & styles
 - fill(r,g,b[,a]) -> self.fill(color) / return current fill state — Done
 - noFill() -> self.no_fill() — Done
 - stroke(r,g,b[,a]) -> self.stroke(color) — Done
 - noStroke() -> self.no_stroke() — Done
 - strokeWeight(w) -> self.stroke_weight(w) — Done
 - strokeCap()/strokeJoin() -> self.stroke_cap()/self.stroke_join() — Partial (caps/joins emulated; full miter math T503)

Transforms & matrix stack
 - translate(x,y) -> self.translate(x, y) — Todo
 - rotate(angle) -> self.rotate(angle)  (document angleMode — radians vs degrees) — Todo
 - scale(sx[, sy]) -> self.scale(sx, sy=None) — Todo
 - pushMatrix()/popMatrix() -> self.push() / self.pop() (or push_matrix/pop_matrix) — Todo

Mode helpers
 - rectMode(CORNER|CENTER|CORNERS) -> self.rect_mode('corner'|'center'|'corners') — Done (corner/center)
 - ellipseMode(CENTER|RADIUS|CORNER) -> self.ellipse_mode(...) — Done (center/corner)
 - imageMode(CORNER|CENTER) -> self.image_mode(...) — Todo
 - angleMode(RADIANS|DEGREES) -> self.angle_mode('radians'|'degrees') — Todo

Image & pixel operations
 - loadImage(path) -> self.load_image(path) returning an Image/Surface object — Done (Assets-backed loader + fallbacks)
 - image(img, x, y, w=None, h=None) -> self.image(img, x, y, w=None, h=None) — Done
 - imageMode(...) -> self.image_mode(...) — Todo
 - pixels[] / loadPixels() / updatePixels() -> self.load_pixels(), self.update_pixels(), pixel buffer access via Image object — Todo
 - get(x,y) / set(x,y,color) -> self.get_pixel(x,y) / self.set_pixel(x,y,color) — Todo

Offscreen rendering (PGraphics / ofFbo)

The ability to render into an offscreen buffer (often called PGraphics in Processing or ofFbo in openFrameworks) is essential for layering, caching expensive draws, post-processing, and rendering to images or textures.

Suggested PyCreative API:
 - `pg = self.create_graphics(width, height)` -> returns an offscreen `OffscreenSurface` object — Done
 - `pg.begin()` / `pg.end()` or context-manager `with pg:` to set the offscreen surface as the current draw target — Done (context manager supported)
 - `pg.clear(color)` / `pg.ellipse(...)` / `pg.rect(...)` -> draw into the offscreen buffer using the same primitives — Done
 - `self.image(pg, x, y)` or `self.blit(pg, x, y)` -> blit the offscreen buffer onto the main surface — Done (`image()` preferred; blit/backcompat present)
 - `pg.get_image()` -> return an Image object or PIL-compatible representation for saving or pixel access — Todo
 - `pg.save(path)` -> save contents to disk as PNG/JPEG — Done (best-effort `save()` implemented)

Behavioral notes and acceptance:
- Offscreen surfaces should use the same coordinate conventions as the main canvas.
- Creating and destroying offscreen buffers should be explicit; provide `pg.close()` if necessary.
- Blitting an offscreen surface should behave like drawing an image with optional alpha/composite modes.
- Support resizing or recreating offscreen buffers; document performance tradeoffs and recommend reusing buffers for repeated draws.

Examples
- `examples/offscreen_example.py` should demonstrate:
	- creating a `PGraphics`/offscreen surface
	- drawing complex content into it once and reusing the cached buffer each frame
	- applying a simple post-process (e.g., blur shader or pixel manipulation) and blitting the result to the main canvas

Testing ideas
 - Unit test that a `Surface` created via `create_graphics` receives primitive draw calls (mock the underlying pygame surface) — Partial
 - Integration test that draws to an offscreen surface, blits to main canvas, and verifies pixel values at expected coordinates — Partial (tests exist for basic blit/offscreen behavior)


Typography
- text(str, x, y) -> self.text(str, x, y, font=None)
- textSize(s) -> self.text_size(s)
- textAlign(LEFT|CENTER|RIGHT) -> self.text_align(...)
- createFont(name, size) / loadFont -> self.load_font(name_or_path, size)

Input & events
- keyPressed(), keyReleased(), keyTyped() -> self.on_event(event) unified InputEvent with type/key/mods
- mousePressed(), mouseReleased(), mouseMoved(), mouseDragged() -> self.on_event(event) + helper properties mouse_x/mouse_y/pmouse_x/pmouse_y
- mouseX, mouseY, pmouseX, pmouseY -> self.mouse_x, self.mouse_y, self.pmouse_x, self.pmouse_y

Time, frame control & utilities
- frameRate(fps) -> self.frame_rate(fps)
- frameCount -> self.frame_count
- millis() -> self.millis()
- delay(ms) -> self.delay(ms) (discouraged in code running main loop)

Math & mapping
- random(low, high) -> self.random(low, high) or utilities.random(low, high)
- map(value, start1, stop1, start2, stop2) -> utilities.map(value, ...)
- lerp(start, stop, amt) -> utilities.lerp(...)

Color & constants
- color(r,g,b[,a]) -> color utility or simple tuples (r,g,b) accepted throughout
- predefined constants: PI, TWO_PI, HALF_PI, etc. -> math.pi, utilities.TWO_PI

File I/O & save
- save(filename) / saveFrame() -> self.save(filename) / self.save_frame(pattern)

OpenFrameworks equivalents (high level)
- ofApp::setup/update/draw -> Sketch.setup/update/draw
- ofImage -> Image/Surface wrapper with fast blit
- ofSoundPlayer -> Audio module wrapper for playback

## Implementation Roadmap (high level tasks)

This roadmap breaks the work into focused task groups. Each group includes suggested acceptance criteria and test ideas. Use these to generate tasks.md entries and estimate effort.

1) Core runtime & lifecycle (priority: high)
- Tasks:
	- Implement `Sketch` base class with lifecycle methods: `setup()`, `update(dt)`, `draw()`, `on_event(event)`, `teardown()`.
	- Provide `run()` to start the PyGame loop and manage dt/frame timing and `frame_rate()` enforcement.
- Acceptance:
	- Example sketches run and call lifecycle hooks in order. Unit test: instantiate a Sketch subclass and verify hook invocation order for N frames (headless/mockable).

2) Surface & immediate-mode primitives (priority: high)
- Tasks:
	- Implement `Surface` wrapper and attach drawing primitives to `Sketch` (ellipse, rect, line, point, triangle, quad).
	- Provide default coordinate system and drawing state (fill/stroke/stroke_weight).
- Acceptance:
	- Examples render shapes; primitives accept color tuples and optional stroke/fill overrides. Unit tests: call primitives and assert they modify a backing pixel buffer (mocked) or call underlying PyGame draw APIs with expected args.

3) Drawing state & stack (priority: high)
- Tasks:
	- Implement fill/no_fill, stroke/no_stroke, stroke_weight, push/pop transforms, translate/rotate/scale.
	- Implement rect_mode, ellipse_mode, image_mode, angle_mode.
- Acceptance:
	- Transformations are local to push/pop. Modes affect subsequent primitive coordinate interpretation. Tests for transform math and mode conversions.

4) Images & pixels (priority: medium)
- Tasks:
	- Image load/save, image blit, image resizing, pixel access (load_pixels/update_pixels), image_mode.
- Acceptance:
	- Load an image from disk, blit with/without resize, read/write a pixel and persist changes to an image file (integration test, mocked in unit tests).

5) Text & fonts (priority: medium)
- Tasks:
	- Provide text rendering, text_size, text_align, load_font wrapping Pillow/SDL_ttf as available.
- Acceptance:
	- Render sample text with alignment options into a Surface and assert text metrics and placement.

6) Input abstraction (priority: high)
- Tasks:
	- Unified `InputEvent` layer mapping PyGame events to friendly attributes (`type`, `key`, `pos`, `button`, `mods`).
	- Provide `mouse_x`, `mouse_y`, `pmouse_x`, `pmouse_y`, and keyboard state helpers.
- Acceptance:
	- Input example receives events and `on_event` is called with normalized event objects. Unit tests: create synthetic PyGame events and ensure mapping correctness.

7) Utilities & math helpers (priority: low/medium)
- Tasks:
	- Provide `random`, `map`, `constrain`, `lerp`, color helpers, constants.
- Acceptance:
	- Unit tests for deterministic outputs where possible.

8) Audio & video modules (priority: low)
- Tasks:
	- Wrap platform-friendly audio playback APIs (sounddevice, pygame.mixer) and video frame decoders (ffmpeg + OpenCV) as optional extras.
- Acceptance:
	- Example sketches play a short audio clip; integration tests run in an environment with optional deps installed.

9) Docs, examples, and mapping (priority: ongoing)
- Tasks:
	- Maintain `docs/api-mapping.md`, examples for each subsystem, quickstart, and migration notes.
- Acceptance:
	- Examples runnable; docs contain code snippets and behavior notes.

## Test strategy and next steps
- Use unit tests for pure logic and small integrations with PyGame mocked (for headless CI).
- Provide one integration test that runs the app loop for a few frames in headless mode (mark as integration and optional for CI by default).
- After acceptance for each task group, add an example under `examples/` demonstrating the feature.

---
