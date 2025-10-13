# ADR 0001 — Skia as GPU-first renderer

Status: Accepted

Context
-------
The PyCreative project targets fast, deterministic 2D rendering for creative
coding. Skia (via `skia-python`) provides a mature GPU-backed 2D renderer
that maps well to our needs: anti-aliased shapes, fast compositing, and direct
access to GPU surfaces.

Decision
--------
Adopt `skia-python` as the primary GPU rendering engine. Engines and adapters
will expose a small, testable API that allows sketches to draw using Skia and
composite the result into the display's GL context (currently via pyglet).

Consequences
------------
- Pros:
  - High-quality, GPU-accelerated 2D rendering with a stable API.
  - Smooth path to cross-platform GPU composition (OpenGL-backed surfaces).
  - Good testability: we can render to offscreen FBOs and read back snapshots
    for headless CI tests.

- Cons / Risks:
  - `skia-python` is a binary dependency; CI must use compatible platform
    wheels or have a fallback path for headless tests.
  - Some skia-python builds may not support direct encode-to-data snapshots
    (we observed encodeToData() returning None), so we provide a reliable
    fallback: render into an FBO and read back with glReadPixels.

Implementation notes
--------------------
- Provide an adapter under `src/core/adapters/skia_gl.py` that exposes:
  - render_to_texture(width, height, draw_fn) -> GLuint texture id
  - render_to_png(path, width, height, draw_fn) -> writes a PNG snapshot

- The adapter will:
  - create an OpenGL FBO + texture, create a Skia GrDirectContext tied to
    the OpenGL context, build a Skia surface from the backend render target,
    call the supplied `draw_fn(canvas, width, height)`, flush, and either
    return the GL texture id or perform a readback and write PNG.

- For CI and headless tests, the adapter should provide a readback path that
  doesn't require encodeToData() (glReadPixels fallback).

Notes on the local run that motivated this ADR
---------------------------------------------
- Performed an exploratory run on macOS using the repository venv. Steps:
  - Activated venv: `source venv/bin/activate`
  - Installed dependencies: `pip install skia-python pyglet pillow numpy`
  - Ran a short demo that:
    - Created an OpenGL texture and FBO
    - Created a Skia GrDirectContext (GrDirectContext.MakeGL)
    - Built a Skia surface from the FBO and drew shapes (rect + circle)
    - Flushed Skia to the GL texture
    - Used glReadPixels to snapshot the FBO to `skia_readback.png`

The `skia_readback.png` snapshot was produced at the project root.

Follow-ups
----------
- Implement `src/core/adapters/skia_gl.py` and examples using it.
- Add integration tests that run the adapter and validate produced snapshots
  (mark them as integration or skip when display is unavailable in CI).
- Document system requirements for `skia-python` in `docs/developer/`.
