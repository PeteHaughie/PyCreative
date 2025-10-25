save_frame: behaviour, implementation notes and fallback

This document explains how the `save_frame()` helper is implemented and the guarantees the presenter provides when writing out a PNG image.

Why this exists

Users expect `self.save_frame(path)` to write an on-screen snapshot of the final frame. Because rendering uses a GPU-backed Skia surface (FBO / texture), capturing pixels must happen after the presenter has rendered. There are two call contexts:

- inside draw() (i.e. while the engine is in the draw callback);
- outside draw() (e.g. in input handlers or timers).

Semantic guarantees

- Calls made inside draw(): the request is deferred and processed by the presenter during the subsequent present/render pass so the saved PNG contains exactly what was drawn for that frame.
- Calls made outside draw(): the presenter is asked for an immediate snapshot of the current GPU-backed Skia surface. If the presenter is unavailable or the immediate path fails, the request is queued and will be processed at the next present.
- The implementation is best-effort: failures to capture or write do not raise in user code. Instead, failures are logged at the debug level.

Where the logic lives

- Orchestration: `src/core/engine/snapshot.py`
  - Resolves path templates, chooses a backend, and decides to queue vs attempt immediate present snapshot based on `engine._in_draw`.
  - If `engine._presenter` exists and the call is outside draw(), `snapshot.py` attempts an immediate presenter snapshot and falls back to queueing the request.

- Presenter handling: `src/core/adapters/skia_gl_present.py`
  - `SkiaGLPresenter.render_commands()` processes queued `save_frame` commands after Skia has flushed and GL sync has completed. This ensures the readback sees the final rendered pixels.
  - The presenter prefers a Skia-encoded snapshot (`surf.makeImageSnapshot()` + `encodeToData()`). If that is unavailable or fails, it falls back to a GL readback (`glReadPixels`) and wraps the pixels into a Pillow PNG.
  - The resulting PNG bytes are written atomically: a temporary file is created next to the requested target path and then moved into place via `os.replace()` so partial writes are not left behind.

Fallbacks and failure behavior

- Skia snapshot failure: logged at debug level and the presenter attempts a GL readback.
- GL readback failure: logged at debug level and the save request is skipped. The call does not raise to user code.
- Final write failure: logged at debug level. The temporary file is removed when possible.

Debugging and diagnosing

- Extra diagnostics are available but are disabled by default. The following environment variables enable more invasive debug actions:
  - `PYCREATIVE_DEBUG_LIFECYCLE_DUMP=1` — writes optional diagnostic PNGs (readback dumps) to disk when enabled.
  - `PYCREATIVE_DEBUG_PRESENT=1` — prints present-mode and GL error info to stdout and (when enabled) a small present log is appended to `/tmp/pycreative_present_log.txt`.

Notes for contributors

- Avoid adding unconditional prints or file writes to the presenter: keep diagnostics gated behind environment flags or the logger. Production runs and CI should remain quiet by default.
- When changing the save flow, update these docs and consider adding a focused test that exercises `save_frame()` called from an input handler (non-draw) to verify the immediate-path vs queued-path behaviour. A full integration test may require a display or a headless GL context.
