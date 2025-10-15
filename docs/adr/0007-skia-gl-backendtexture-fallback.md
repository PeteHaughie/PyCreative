# ADR 0007 — Skia GL backend-texture reliability and FBO-attach fallback

Date: 2025-10-14

Status: Accepted

Context
-------
We want to use skia-python's GPU renderer to draw directly into GL textures and present them via pyglet without a GPU→CPU roundtrip. The ideal path is to create a Skia GrBackendTexture from an existing GL texture id and call Surface.MakeFromBackendTexture so Skia writes directly into that texture (true zero-copy).

However, skia-python builds vary across platforms and versions. During testing on macOS with the project's venv, attempts to construct GrBackendTexture with a GrGLTextureInfo either raised TypeErrors or blocked (native-level hang) depending on the constructor signature. Additionally, GrBackendTexture.MakeGL is not always present.

Decision
--------
1. Prefer a robust FBO-attach fallback: bind the existing GL texture id to a freshly-created GL framebuffer (FBO), then create a Skia GrBackendRenderTarget from the FBO (using GrGLFramebufferInfo) and call Surface.MakeFromBackendRenderTarget. This lets Skia render directly into the bound texture without calling GrBackendTexture constructors that may hang.

2. Continue to probe for direct GrBackendTexture constructors at runtime: keep small probe scripts (see docs/developer/skia-gl-probes.md) that detect available constructors. If a safe direct backend-texture constructor exists on a user's environment, prefer it; otherwise use the FBO-attach path.

3. Document the issue and the fallback in developer docs, add CI-friendly probe scripts, and include an agent-facing note so automated agents reuse the same safe approach.

Consequences
------------
- Pros:
  - The FBO-attach method works reliably on the tested macOS/skia-python build.
  - Avoids native-level hangs and platform-specific constructor mismatches.
  - Still avoids CPU readback: Skia draws directly into a GPU texture.

- Cons:
  - Requires temporarily binding the texture to an FBO (cheap on modern GL but an extra GL call).
  - May not be the absolute minimal-zero-copy path supported by some platforms; but it is robust.

References and artifacts
------------------------
- Probe and signature test scripts: `scripts/inspect_skia.py`, `scripts/attempt_backend_texture.py`, `scripts/try_backend_signatures.py`
- Demo: `scripts/test-skia-pyglet-zero-copy.py` (FBO-attach fallback implemented)

Notes
-----
If future skia-python builds provide stable and documented GrBackendTexture constructors or `GrBackendTexture.MakeGL`, the direct backend texture path can be re-enabled via runtime detection. Until then, the FBO-attach method is the project's default safe GPU path.
