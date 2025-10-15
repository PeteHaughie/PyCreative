# ADR 0008 — Presenter shader fallback and GLES support

Status: Proposed

Context
-------
The presenter must display a Skia-rendered offscreen texture into the default
framebuffer. On many platforms the fastest/cleanest approach is a framebuffer
blit (glBlitFramebuffer). When blit is unavailable or when running in a
core-profile context, a shader-based textured-quad is preferred. Legacy
immediate-mode rendering is only a last-resort fallback because it's invalid
in many modern GL profiles.

Problem
-------
OpenGL drivers and contexts vary widely across platforms (macOS, Linux desktop,
Raspberry Pi's OpenGL ES). Shader source compatibility (GLSL version and
semantics) differs: macOS often requires newer or distinct GLSL versions; many
embedded platforms use GLSL ES (GLES) variants. The presenter must pick a
shader variant that will compile on the running context, but we also want a
mechanism to force a variant for testing.

Decision
--------
- Present using glBlitFramebuffer when available and not explicitly forced to
  a different mode.
- If blit is unavailable or skipped, attempt shader-based presentation in
  the following preferred order:
  1. GLSL ES 300 (GLES3) — for GLES3-capable contexts and when `--force-gles`
     is requested by the developer.
  2. GLSL 150 (desktop modern/core) — for modern desktop GL contexts.
  3. GLSL 120 (legacy) — compatibility fallback for older drivers that
     explicitly support legacy GLSL.
- If all shader attempts fail, fall back to immediate-mode textured quad as a
  last resort (may be invalid in core profiles).
- Provide a CLI flag `--force-gles` which forces the presenter to prefer GLES
  variants first (useful for testing GLES code paths on desktop).

Consequences
------------
- The presenter is robust across platforms by attempting multiple shader
  variants.
- Developers can test GLES code paths by using `--force-gles` even on desktop
  machines.
- The runtime now includes diagnostic logging for shader compile/link logs and
  GL errors to aid debugging.

Notes
-----
- This ADR complements the presenter's `SkiaGLPresenter._variant_ordering`
  helper (test-friendly) and a small suite of unit tests that assert ordering
  behaviour.
