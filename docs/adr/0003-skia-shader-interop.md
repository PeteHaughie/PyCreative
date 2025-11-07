# 0003  Skia GPU ↔ GL shader interop

Date: 2025-11-07

Status: Accepted

Context
-------
PyCreative exposes a PCShader API that allows sketches to supply fragment
shaders (and optionally light-weight vertex shaders). Many shaders expect
to sample a source image (the Processing `image()` / `iChannel0` pattern)
and output a processed image. On platforms/drivers the path that compiles
and links user shaders can be fragile due to attribute-name optimization,
GLSL version mismatches, and platform differences (desktop GLSL vs GLES).

Decision
--------
Implement an opt-in intermediate GL-render path that:

- Compiles/links the user's fragment shader (with conservative GLSL
  variant fallbacks) in a GL context.
- Renders the shader into an intermediate GL texture attached to an
  FBO (draw a fullscreen triangle using gl_VertexID when attribute
  names are unavailable).
- Wraps the resulting GL texture into a Skia GPU backend object when
  supported (via skia.GrGLTextureInfo + skia.GrBackendTexture) and
  draws that Skia image into the presenter's Skia surface.
- If wrapping is unsupported on the current platform, fall back to a
  GPU blit into the presenter's FBO (avoids CPU readbacks).

This flow is gated behind the environment variable
`PYCREATIVE_DEBUG_ENABLE_SHADER_IMAGE` while we validate correctness
and portability.

Consequences
------------

- Pros:
  - Keeps Skia as the single compositor (draw/compose semantics remain
    unchanged). The shader is used only as a processing step producing
    a GPU texture, which Skia can draw normally.
  - Avoids attribute-name fragility by using an attributeless vertex
    fallback where necessary (gl_VertexID). This is robust across
    driver optimizations.
  - Preserves performance by staying on-GPU: wrapping a GL texture into
    Skia or blitting on-GPU avoids expensive CPU round-trips.

- Cons / Risks:
  - Skia<->GL interop depends on skia-python and platform support for
    backend texture APIs. Not all environments may support this.
  - Correct GL ↔ Skia context management and GL state save/restore is
    required to avoid interfering with other rendering.
  - Additional test surface area (platform-specific failures, macOS
    core profile VAO requirements, etc.).

API & Implementation Notes
--------------------------

1. Opt-in flag
   - Use `PYCREATIVE_DEBUG_ENABLE_SHADER_IMAGE=1` to enable the
     intermediate-texture shader-image path. Keep the default path
     unchanged until tests validate stability.

2. Presenter API additions
   - Add SkiaGLPresenter._render_shader_to_gl_texture(shader, image_bytes, size)
     — compiles (if needed) and renders the shader into a GL texture
     attached to an FBO. Returns the GL texture id.
   - Add SkiaGLPresenter._wrap_gl_texture_in_skia(tex_id, w, h)
     — attempts to construct skia.GrGLTextureInfo and skia.GrBackendTexture
     and returns a Skia Image or None on failure.

3. Fallbacks
   - If wrapping to a Skia backend texture fails, blit the texture into
     the presenter's FBO using GL (no CPU readback).
   - If blit fails, fall back to existing Skia replay behaviour (no shader
     applied) and surface will remain consistent.

4. Shader authoring guidance
   - Prefer `#version 150` or `#version 300 es` in shaders.
   - If the shader expects vertex attributes, prefer supplying a simple
     vertex shader or rely on the attributeless fallback.

Testing
-------

- Unit: small headless test that compiles a fragment shader that samples
  iChannel0 and produces a known tint. Render to a small (16×16)
  intermediate texture and verify the center pixel is the expected color.
- Integration: run `examples/hello_world/shader_sketch.py` with
  `PYCREATIVE_DEBUG_ENABLE_SHADER_IMAGE=1` and assert the produced
  snapshot contains expected tinted pixels.

Notes
-----

This ADR records the initial plan and minimal API contract. The
implementation will be opt-in and iterated on with tests. If skia-python
proves unable to wrap backend textures reliably across environments we
will default to an on-GPU blit fallback and only enable wrapping where
the probe succeeds.

Related ADRs: 0001 (Skia GPU first), 0002 (Public shims and package split)
