# Feature Specification: Batteries-Included Creative Coding Framework for Python

**Feature Branch**: `dev-refactor`
**Created**: 28 September 2025  
**Status**: Draft  
**Input**: User description: "Build a 'batteries included' creative coding framework for Python built around PyGame designed for rapid prototyping of visual, audio, and interactive projects while remaining lightweight and extensible. The API should be idiomaticly inspired by Processing and openFrameworks."

## Execution Flow (main)
```
1. Parse user description from Input
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
An artist, educator, or developer wants to quickly prototype a visual, audio, or interactive project in Python using a simple, ergonomic API. They expect to be able to create sketches, handle input, and render graphics with minimal setup, and optionally extend the framework for advanced use cases.

### Acceptance Scenarios
1. **Given** a new user with Python installed, **When** they install the framework and run a minimal sketch, **Then** a window opens and displays graphics as described in their code.
2. **Given** a user wants to add audio or video playback, **When** they use the relevant API, **Then** the media plays as expected in their sketch.
3. **Given** a user wants to handle keyboard or mouse input, **When** they implement the input hooks, **Then** the sketch responds interactively.

### Edge Cases
- What happens when the user runs the framework on a system without PyGame installed? The framework MUST fail with a clear error message. Installation instructions are provided in the main project README. No auto-install or prompt is required at MVP stage.
- How does the system handle unsupported media formats? If a codec is unsupported echo out the problem to the terminal and close the sketch safely.
- What if the user requests features (e.g., shaders, video) that require optional dependencies? All dependencies, including optional extras, MUST be specified in pyproject.toml and installed with the app. If a required dependency is missing, the framework MUST fail with a clear error message. No runtime installation or prompts are required.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST allow users to create and run visual sketches with minimal code.
- **FR-002**: System MUST provide ergonomic APIs for graphics primitives (rect, ellipse, line, image, etc.).
- **FR-003**: System MUST support input handling for keyboard and mouse events.
- **FR-004**: System MUST offer optional modules for audio and video playback.
- **FR-005**: System MUST be extensible for advanced features (e.g., shaders, custom UI widgets).
- **FR-006**: System MUST provide clear error messages for missing dependencies or unsupported features.
- **FR-007**: System MUST be lightweight and not require unnecessary dependencies by default.
- **FR-008**: System MUST document all public APIs with examples.
- **FR-009**: System MUST support rapid prototyping and live coding workflows.
- **FR-010**: System MUST be inspired by Processing and openFrameworks in API design and usability.
   - Acceptance criteria:
      - Provide a `Sketch` base class with lifecycle hooks: `setup()`, `update(dt)`, `draw()`, `on_event(event)`, and `teardown()`.
      - Provide immediate-mode drawing primitives (`rect`, `ellipse`, `line`, `image`) accessible via a `Surface` or directly on the `Sketch` instance, using a consistent default coordinate system.
      - Expose a simple sizing API such as `size(width, height, fullscreen=False)` (or equivalent) that mirrors common Processing usage.
      - Include a runnable example in `examples/` (e.g., `examples/hello_sketch.py`) that demonstrates parity with a basic Processing sketch (moving ellipse using `setup`/`draw`).
      - Publish a short mapping document (`docs/api-mapping.md`) that describes how core APIs correspond to Processing/openFrameworks concepts.
   - Non-normative note: The goal is API ergonomics and idiomatic parity only — do not copy or reuse source code from Processing or openFrameworks. Implement behavior and ergonomics that make migration/learning straightforward for users familiar with those frameworks.
- **FR-011**: System MUST allow users to extend or override core primitives and event handling.
- **FR-012**: System MUST provide basic asset management and hot-reload for media files.
- **FR-013**: System MUST provide a CLI for running sketches from the command line.
- **FR-014**: System MUST support unit and integration testing for core features.

### Key Entities
- **Sketch**: Represents a user project or script, encapsulating setup, update, draw, and event hooks.
- **Surface**: Represents the drawing context for graphics primitives.
- **InputEvent**: Encapsulates keyboard and mouse events.
- **Asset**: Represents media files (images, audio, video) used in sketches.

---

## Graphics module split and migration plan (developer-facing)

Rationale
- The current `src/pycreative/graphics.py` is monolithic: it mixes the `Surface`
   façade, drawing primitives, pixel helpers, blend algorithms, shape math,
   and utility helpers. This makes reviews, optimizations (numpy/fast paths), and
   targeted testing harder. The project will incrementally split this file into a
   small package of focused modules while preserving the public API
   (`from pycreative.graphics import Surface`).

Decision notes
- Module name containing pixel helpers: `pixels.py` (explicit decision: not `pixel_helpers.py`).
- Keep the `Surface` class as the public façade and re-export it from the package root so external imports remain stable.

Target package layout (final state)
- `src/pycreative/graphics/`
   - `__init__.py`        # re-export public API (`Surface`) for backwards-compat
   - `surface.py`         # Surface class core, state + orchestration
   - `primitives.py`      # rect, ellipse, line, polygon, etc.
   - `image.py`           # image(), img(), image_mode(), tint() orchestration
   - `blending.py`        # blend algorithms and `apply_blit_with_blend()`
   - `pixels.py`          # get_pixels, set_pixels, get_pixel, set_pixel, pixels(), PixelView
   - `shape_math.py`      # bezier flattening, curve helpers, begin/vertex/end helpers
   - `utils.py`           # `_get_temp_surface` cache & small utilities
   - `text.py`            # text rendering convenience wrapper (optional)

API contracts (short)
- `blending.apply_blit_with_blend(dst: pygame.Surface, src: pygame.Surface, bx:int, by:int, mode:str, tint:tuple|None=None) -> None`
   - Apply tint (if present) and blend `src` into `dst` at `(bx,by)` using Processing-style modes. Fast-paths should use `pygame.BLEND_RGBA_*`; SCREEN/DIFFERENCE/EXCLUSION must have deterministic per-pixel fallbacks.
- `pixels.get_pixel(surface, x, y) -> tuple[int,...]` returns (r,g,b) or (r,g,b,a) depending on destination surface.
- `pixels.get_pixels(surface) -> PixelView` and `pixels.set_pixels(surface, arr)` mirror current semantics and allow future surfarray/numpy fast-paths.

Staged migration plan (incremental, test-driven)
1. Stage 0 — Baseline: add/expand tests for blending/pixels and record `pixels.py` decision in this spec. Run full test suite and capture baseline.
2. Stage 1 — Extract `blending.py`: move blending/tint math into `blending.py`, expose `apply_blit_with_blend`, keep a delegating call in the existing `graphics.py` to minimize changes. Run blend tests.
3. Stage 2 — Extract `pixels.py`: move pixel helpers and `PixelView` into `pixels.py`. Replace direct pixel-access usages with calls into this module (or small delegators on `Surface`). Run pixel-related tests.
4. Stage 3 — Extract `primitives.py` and `shape_math.py`: move primitive drawing and shape-building math into focused modules; have `Surface` delegate to them.
5. Stage 4 — Extract `image.py` and wire `apply_blit_with_blend` for image drawing (scale/rotozoom/image_mode handled here); run image/offscreen examples headlessly.
6. Stage 5 — Finalize: move the `Surface` class into `surface.py`, add `__init__.py` to re-export `Surface`, and remove the old monolith after tests are green.

Quality gates at each stage
- Run unit tests relevant to the changed module (e.g., `tests/test_blend_modes.py` after Stage 1).
- Run the full test suite (`pytest -q`) before and after Stage 5.
- Smoke-run representative examples headless (e.g., `pycreative examples/offscreen_example.py --headless --max-frames 3`).
- Run linter (`ruff src/ tests/`) and address new issues introduced by imports.

Tests to add or expand (priority)
- Per-mode blending unit tests (opaque and semi-transparent sources) — `tests/test_blend_modes.py` already added; expand to include alpha and tint+blend cases.
- Pixel round-trip tests: `get_pixels`/`set_pixels` and `pixels()` context manager.
- Bezier/curve flattening tests for `shape_math` (accuracy and deterministic sampling).

Risks & mitigations
- Risk: circular imports when splitting. Mitigation: keep `blending.py` and `pixels.py` dependent only on plain `pygame.Surface` and low-level data; `Surface` remains the orchestrator that imports helpers.
- Risk: behavior change during movement. Mitigation: keep delegating stubs in the original module until tests pass; move in small commits.

Developer guidance
- Keep each commit small and run the tests frequently.
- Document any public API signature changes in `docs/api-mapping.md` and update examples that rely on internals (examples should not rely on private helpers).


---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous  
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [ ] Review checklist passed

---
