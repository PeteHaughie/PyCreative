# Tasks: Batteries-Included Creative Coding Framework for Python

**Input**: Design documents from `/specs/dev-refactor/`
**Prerequisites**: plan.md (required)

## Execution Flow (main)
```
1. Load plan.md from feature directory
2. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: integration tests, unit tests
   → Core: models, services, CLI commands
   ````markdown
   # Tasks: Batteries-Included Creative Coding Framework for Python

   **Input**: Design documents from `/specs/dev-refactor/`
   **Prerequisites**: plan.md (required)

   ### Conventions
   - Task ID format: `T###` (T100+ reserved for implementation roadmap)
   - `[P]` marker: safe to run in parallel (different files, no direct dependencies)
   - Each task must reference the target file(s) to change and include acceptance criteria.

   ---

   ## Phase 1 — Core runtime & lifecycle (HIGH)

   - [*] T100 Implement `Sketch` base class and runtime loop (src/pycreative/app.py)
      - Files: `src/pycreative/app.py`
      - Acceptance:
         * `Sketch` exposes lifecycle hooks: `setup()`, `update(dt)`, `draw()`, `on_event(event)`, `teardown()`.
         * `run()` starts a PyGame loop, calls hooks in order, enforces `frame_rate()`.
         * Example `examples/sketch-lifecycle_example.py` runs without raising exceptions for 5 frames (integration test).

   - [*] T101 Add package exports and basic package metadata (src/pycreative/__init__.py)
      - Files: `src/pycreative/__init__.py`
      - Acceptance: `from pycreative import Sketch` works; `pycreative.input` importable.

   ---

   ## Phase 2 — Surface & immediate-mode primitives (HIGH)

   - [*] T200 Create `Surface` wrapper and attach to `Sketch` (src/pycreative/graphics.py)
      - Files: `src/pycreative/graphics.py`, update `src/pycreative/app.py` to use Surface
      - Acceptance:
         * Primitive functions: `ellipse`, `rect`, `line`, `point`, `triangle`, `quad` callable on `Sketch` or `Sketch.surface`.
         * Unit test: primitives call `pygame.draw.*` with expected args (mock pygame.draw) or manipulate a test surface pixel buffer.
         * Example updated: `examples/graphics_example.py` shows primitives.

   - [*] T201 Implement drawing state helpers (fill/no_fill, stroke/no_stroke, stroke_weight) (src/pycreative/graphics.py)
      - Files: `src/pycreative/graphics.py`
      - Acceptance: state persists across calls until changed; tests verify color application.

   - [*] T202 Implement offscreen surfaces / PGraphics / ofFbo (src/pycreative/graphics.py)
      - Files: `src/pycreative/graphics.py`, update `src/pycreative/app.py` to add `create_graphics()` helper
      - Acceptance:
         * `create_graphics(w,h)` returns a `Surface`-like object that supports `begin()`/`end()` or a context manager and uses the same drawing primitives.
         * `blit`/`image` supports drawing the offscreen buffer onto the main surface with alpha/composite modes.
         * `pg.get_image()` returns an Image-like object for pixel access and `pg.save(path)` writes PNG.
         * Unit test: draw to offscreen surface, blit to main surface, and assert expected pixel values at test coordinates (use mocked surfaces or headless SDL when possible).
         * Example: `examples/offscreen_example.py` demonstrates caching expensive draws in an offscreen buffer and reusing it.

   ---

   ## Phase 3 — Transformations & modes (MEDIUM)

   - [ ] T300 Implement transforms and matrix stack: `push()`, `pop()`, `translate`, `rotate`, `scale` (src/pycreative/graphics.py)
      - Acceptance: transform math correct (unit tests for transformed coordinates).

   - [ ] T301 Implement mode helpers: `rect_mode`, `ellipse_mode`, `image_mode`, `angle_mode` (src/pycreative/graphics.py)
      - Acceptance: primitives respect modes; tests for coordinate interpretation.

   ---

   ## Phase 4 — Input abstraction & helpers (HIGH)

   - [ ] T400 Normalize PyGame events into `pycreative.input.Event` (src/pycreative/input.py) [P]
      - Files: `src/pycreative/input.py`
      - Acceptance: `Event.from_pygame()` maps key/mouse/motion to unified fields; unit tests create synthetic events and assert mapping.

   - [ ] T401 Add mouse/key helper properties on `Sketch` (`mouse_x`, `mouse_y`, `pmouse_x`, `pmouse_y`, `keys_down`) (src/pycreative/app.py)
      - Acceptance: values updated during event dispatch; example `examples/input_example.py` demonstrates usage.

   ---

   ## Phase 5 — Images, pixels & typography (MEDIUM)

   - [ ] T500 Image load/save API and `Image` wrapper (src/pycreative/graphics.py or src/pycreative/assets.py)
      - Acceptance: load an image, blit to surface, read/write pixel, unit tests for API.

      - [ ] T502 Refactor asset loader to unified `load()` API (MEDIUM)
         - Files: `src/pycreative/assets.py`, `src/pycreative/app.py`, `tests/` (new)
         - Purpose: Provide a single, openFrameworks-style `load(path)` entrypoint on the Assets manager that detects and returns the appropriate asset type (Image, Sound, Video, Font, etc.), centralizes path resolution (sketch/data, sketch dir, project assets), and preserves caching and backward-compatible convenience methods (`load_image`, `load_media`).
         - Acceptance:
            * `Assets.load(path: str)` exists and returns a typed object depending on file extension (e.g., pygame.Surface for images, Sound object for audio) or a light wrapper exposing common methods.
            * `Assets.load_image(path)` and `Assets.load_media(path)` remain and internally call `load()` (no duplication of resolution logic).
            * Path resolution: resolves `sketch_dir/data/<path>` then `sketch_dir/<path>` then project-level asset folders; tests cover each resolution case.
            * Caching: repeated calls to `Assets.load(path)` return the identical cached object instance (where appropriate) unless explicitly bypassed.
            * Errors: missing/unsupported assets return `None` and emit a clear warning via the logging system (no uncaught exceptions during normal example runs).
            * Examples: update `examples/graphics_example.py` (or add a minimal example) to use `Sketch.load_image()` which delegates to `Assets.load()` and works in headless mode.
            * Tests: unit tests validate resolution order, caching behavior, and type dispatch for at least image and audio file extensions (mocking disk files or using temporary fixtures).
         - Subtasks:
            1. Design the `load()` contract: supported extensions, return types/wrappers, and caching semantics.
            2. Implement `Assets.load()` and refactor existing `load_image`/`load_media` to delegate to it.
            3. Add logging (use Python `logging`) instead of print statements for debug/info/error messages; make verbosity configurable.
            4. Add unit tests covering resolution, caching, and fallback behavior; mock pygame loads where needed.
            5. Update `Sketch.load_image()` and any surface helpers to prefer `Assets.load()` path.
            6. Update examples to call the new unified API and remove any ad-hoc image path logic.
         - Notes:
            * Keep the change backward-compatible: existing public convenience functions should still work.
            * Consider a small compatibility shim that warns when callers use legacy code paths so maintainers can deprecate them later.

      - [ ] T503 Investigate precise cap/join rendering and miter limits (LOW / backlog)
         - Files: `src/pycreative/graphics.py`, `specs/dev-refactor/notes.md` (new)
         - Purpose: Research and prototype options for accurate line caps and joins (miter calculations, bevel, round joins) and propose a performant implementation strategy that avoids slow CPU-bound backends like pycairo.
         - Acceptance:
            * A short design note created under `specs/dev-refactor/notes.md` comparing possible approaches: pure-Pygame geometry, Moderate-GL/GL shader stroke, signed-distance-field shaders, and small C extensions.
            * Prototype code (non-blocking) showing one feasible approach with estimated performance trade-offs.
            * Recommendation for a path forward (implement geometry-based miter/bevel in Python; or add optional native extension / moderate-GL backend) and a rough plan with estimated effort.
         - Notes: This is a research/backlog item. For now we keep the lightweight emulation in `Surface.polyline()` and expose `set_line_cap`/`set_line_join` as API hooks.

      - [ ] T504 Adaptive subdivision for bezier/curve flattening (MEDIUM)
         - Files: `src/pycreative/graphics.py`
         - Purpose: Replace or augment the current uniform sampling flatteners with an adaptive subdivision algorithm that tessellates cubic Beziers and Hermite/Catmull‑Rom curve segments to meet a configurable pixel/tolerance threshold.
         - Acceptance:
            * Add an adaptive flattening routine used by `bezier()`/`end_shape()` and optionally `curve()` that subdivides until segments are within a flatness/tolerance metric (e.g., chord error or distance-to-control-point heuristics).
            * Expose configuration API: `bezier_tolerance(float)` and `curve_tolerance(float)` (defaults provided) and keep legacy `bezier_detail()`/`curve_detail()` for fixed-sample fallback.
            * Unit tests that demonstrate fewer segments for low-curvature curves and denser sampling around high-curvature regions; visual regression example saved under `examples/` showing adaptive vs uniform sampling.
            * Performance guardrails: ensure worst-case subdivisions are capped (max recursion depth or max segments) to avoid pathological geometry blow-ups.
         - Notes / Next steps:
            1. Implement adaptive subdivision for cubic Beziers (smallest surface area) first, using the recursive midpoint subdivision with flatness test (distance from control points to chord or angle-based test).
            2. Add optional adaptive path for Hermite/Catmull‑Rom by converting small curve segment to a Bezier equivalent or adding a separate flatness test.
            3. Add tests that mock/tune tolerance and compare segment counts vs the current uniform sampler; add a short example `examples/bezier_adaptive_example.py` that writes a side-by-side PNG.
            4. Consider exposing a global switch (e.g., `Surface.adaptive_flattening = True`) to enable/disable runtime behavior for deterministic tests.

      - [ ] T510 Image pixel-array helpers (copy-based) (MEDIUM)
         - Files: `src/pycreative/graphics.py`, `tests/test_pixels.py`, `docs/pixels.md`, `examples/pixels_example.py`
         - Purpose: Provide safe, copy-based pixel array methods for `Surface`/`OffscreenSurface` enabling reading and writing full-image arrays and single-pixel access.
         - Acceptance:
            * Implement `get_pixels()` and `set_pixels(arr)` on `Surface`/`OffscreenSurface`.
              - `get_pixels()` returns an array shaped (height, width, channels) with dtype uint8 (channels 3 or 4 depending on alpha support).
              - `set_pixels(arr)` accepts arrays of shape (h,w,3) or (h,w,4) and writes into the surface, converting formats as needed.
            * Implement `get_pixel(x,y)` and `set_pixel(x,y,color)` for scalar access.
            * Implementation should prefer `pygame.surfarray`/numpy when available and fall back to `pygame.PixelArray` when not.
            * Add unit tests that exercise read/write roundtrips and per-pixel access.
            * Keep default behavior copy-based (no in-place view) to avoid surprising mutability.
         - Notes:
            * Normalize API to return (H,W,C) arrays regardless of pygame's internal (W,H,C) convention. Document this choice in `docs/pixels.md`.
            * Clamp and coerce incoming arrays to uint8 and valid channel counts.

      - [ ] T511 Pixel tests & CI integration (LOW)
         - Files: `tests/test_pixels.py`, updates to `pytest.ini` (if needed)
         - Purpose: Provide deterministic unit tests for the pixel helpers that run in headless CI.
         - Acceptance:
            * Tests include: single-pixel get/set, full-array roundtrip, shape/format validation, fallback path when numpy unavailable (mocked), and save/load roundtrip to disk.
            * Mark any integration tests that require display or real filesystem under `integration` marker.

      - [ ] T512 Docs: Pixel API and example (LOW)
         - Files: `docs/pixels.md`, `docs/README.md` (pointer), `examples/pixels_example.py`
         - Purpose: Document the pixel-array API, examples for common operations, and notes about performance and in-place locking.
         - Acceptance:
            * `docs/pixels.md` describes `get_pixels`, `set_pixels`, `get_pixel`, `set_pixel` semantics, data shapes, and examples.
            * `examples/pixels_example.py` demonstrates reading an image into an array, modifying it, and saving the result.

      - [ ] T513 PImage wrapper & Assets integration (MEDIUM)
         - Files: `src/pycreative/graphics.py`, `src/pycreative/assets.py`, `tests/` (new)
         - Purpose: Implement a small `Image` wrapper (PImage-like) that exposes pixel arrays via `image.pixels` and integrates with `Assets.load()`.
         - Acceptance:
            * `Image.load(path)` and `Assets.load_image()` return an `Image` object exposing `.pixels` (copy-based access) plus `.save(path)`.
            * Backwards compatibility: `Sketch.load_image()` continues to return a pygame.Surface when called without the `Image` wrapper unless explicitly requested.
            * Tests and an example demonstrating `Image` usage are added.
         - Notes:
            * This task is intentionally larger and depends on T510/T511/T512 being complete.

   - [ ] T501 Text rendering helpers (src/pycreative/graphics.py)
      - Acceptance: `text`, `text_size`, `text_align` map to SDL_ttf/Pillow where available; example `examples/text_example.py`.

   ---

   ## Phase 6 — Utilities & math helpers (LOW)

   - [ ] T600 Provide `random`, `map`, `constrain`, `lerp`, color helpers (src/pycreative/utils.py)
      - Acceptance: Unit tests for mapping/lerp behavior and deterministic seeds.

     - [ ] T601 Support Processing-style single-argument `background`/`clear` shorthand (LOW)
       - Files: `src/pycreative/graphics.py`, `src/pycreative/app.py`, `tests/test_clear_hsb.py`, `docs/usage.md`
       - Purpose: Allow `clear(value)` or `background(value)` to be used as a grayscale/brightness shorthand when `color_mode('HSB')` is active, matching Processing behavior and simplifying ports.
       - Acceptance:
          * When `color_mode('HSB', h_max, s_max, v_max)` is active, a single numeric argument to `clear()` or `background()` is interpreted as a brightness/gray value (equivalent to `clear((0, 0, value_norm))` where `value_norm` is normalized to the V channel using `v_max`).
          * Existing three-argument `clear((h,s,v))` behavior remains unchanged.
          * Add unit tests demonstrating both single-arg and triple-arg clears produce expected pixels under HSB mode.
          * Update short usage note in `docs/usage.md` (or `docs/quickstart.md`) describing the shorthand.
       - Notes:
          * Low priority — nice-to-have for smoother Processing ports; do not block higher-priority core tasks.
          * Implementation must be backward-compatible; prefer explicit opt-in behavior (only apply shorthand when a single numeric arg is passed).

   ---

   ## Phase 7 — Audio & Video (OPTIONAL / LOW)

   - [ ] T700 Add optional audio playback wrapper (extras in pyproject.toml) (src/pycreative/audio.py)
   - [ ] T701 Add video frame ingestion and decoding helpers (src/pycreative/video.py)

   ---

   ## Phase 8 — Docs, examples & CI (ONGOING)

   - [ ] T800 Add `examples/` for each subsystem (graphics, input, audio, video, text)
   - [ ] T801 Add integration tests for headless CI (mock pygame or use SDL dummy drivers)
   - [ ] T802 Publish `docs/api-mapping.md` and quickstart `docs/quickstart.md`

   ---

   ## Task ordering & dependencies
   - T100 -> T200 -> T300 (core before transforms)
   - Input tasks (T400/T401) can run in parallel with graphics implementation (T200) but tests should exist first.
   - T500/T501 depend on T200 (Surface implementation).

   ## How to use
   1. Pick a task (start with the lowest-numbered unimplemented task).
   2. Run the scaffolder to create feature stubs if needed: `python scripts/create_feature.py <slug> "Title"`.
   3. Implement code and tests; commit after each task.
   4. Run tests (unit first, then integration).

   ---

   *End of tasks.md*  
   ````
