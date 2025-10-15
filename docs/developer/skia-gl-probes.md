# Skia GL interop probes and fallback guidance

This document explains how to probe the installed `skia-python` for GL interop capabilities, reproduce the `GrBackendTexture` hang observed on some builds, and the recommended runtime fallback strategy used by the project.

Why this exists
---------------
Different `skia-python` builds expose slightly different APIs and may be missing helper constructors (for example `GrBackendTexture.MakeGL`) or have pybind11 constructor signatures that block/hang at the native layer when invoked with the wrong argument shapes. To make GPU rendering robust across machines and CI, we prefer a runtime-detected safe path.

Probe scripts (already in the repo)
---------------------------------
- `scripts/inspect_skia.py` — prints which skia symbols are present (GrDirectContext, GrGLTextureInfo, GrBackendTexture, GrMipmapped, etc.). Use this to quickly assess the available API surface.
- `scripts/attempt_backend_texture.py` — isolated probe that creates a pyglet GL context, creates a GL texture, constructs a `GrGLTextureInfo`, then attempts `GrBackendTexture(...)` and `Surface.MakeFromBackendTexture`. The script prints fine-grained traces before and after each call so you can see where it blocks.
- `scripts/try_backend_signatures.py` — runs multiple candidate constructor signatures in isolated subprocesses with timeouts (safe for CI) to detect which forms raise errors vs hang.

Recommended runtime strategy
---------------------------
1. Run `inspect_skia.py` during startup (or lazily on first GPU drawing) to detect presence of `GrBackendTexture`, `GrGLTextureInfo`, and `GrBackendTexture.MakeGL`.
2. If the direct `GrBackendTexture` constructor forms are present, optionally run a short timeout-limited probe (similar to `try_backend_signatures.py`) to confirm they succeed in this environment.
3. If direct constructors appear unreliable or blocked, use the FBO-attach fallback:
   - Create a framebuffer, attach the existing GL texture id to `GL_COLOR_ATTACHMENT0`.
   - Make a `GrBackendRenderTarget` using `GrGLFramebufferInfo(fbo_id, format)`.
   - Call `Surface.MakeFromBackendRenderTarget` and draw.
4. Unbind the framebuffer and present the texture in the window (the texture is the same GPU resource Skia wrote into).

Practical notes
---------------
- The FBO-attach path avoids native-level hangs observed when constructing `GrBackendTexture` with `GrGLTextureInfo` on some macOS builds.
- It still avoids a GPU->CPU roundtrip: Skia draws on the GPU into the texture, and we display that texture directly.
- The overhead is only the framebuffer bind/unbind and creation of a small `GrBackendRenderTarget` object; this is cheap compared to readback.

How to reproduce the original problem
-----------------------------------
1. Activate the project venv and run the probe scripts (see `scripts/try_backend_signatures.py`) on macOS or the target environment.
2. Observe that some constructor signatures will time out (hang) or cause TypeError messages describing the supported pybind11 signatures.

When to revisit
----------------
If future `skia-python` releases expose robust, documented `GrBackendTexture` constructors or `MakeGL`, we can reintroduce the direct backend texture path behind a runtime feature gate.

Files to inspect in this repo
----------------------------
- `test-skia-pyglet-zero-copy.py` — demo showing FBO-attach fallback.
- `scripts/inspect_skia.py`, `scripts/attempt_backend_texture.py`, `scripts/try_backend_signatures.py` — probe utilities.
