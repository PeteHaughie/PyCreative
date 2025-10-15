Presenter GLSL variants, debugging and testing
===============================================

Overview
--------
The presenter uses a GPU-backed Skia surface to render recorded graphics
commands into a texture. To present that texture to a window it prefers
`glBlitFramebuffer` when available. When blit is not used, the presenter will
attempt a shader-based textured-quad. Shader sources differ by GLSL version
and profile (desktop modern, legacy, GLES). This document explains the
variants, how the presenter selects them, and how to debug failures.

Supported shader variants (preferred order)
-------------------------------------------
- GLES 3.0 — GLSL ES 300 (`#version 300 es`). Preferred on GLES3-capable
  contexts, or when `--force-gles` is supplied.
- Desktop modern — GLSL 150 (`#version 150`). Preferred on modern desktop
  GL contexts.
- Legacy — GLSL 120 (`#version 120`). Compatibility fallback for older
  implementations.

Forcing GLES for testing
------------------------
Use the CLI flag `--force-gles` to force the presenter to prefer the GLES
variant first. This is useful when you want to exercise GLES code paths on a
desktop machine that otherwise prefers desktop GLSL.

Debugging shader failures
-------------------------
The presenter emits `logging.debug` messages for:
- Shader compile logs (GL shader info log)
- Program link logs (GL program info log)
- Created resource IDs (program, VBO, VAO)
- GL errors near resource creation and after draw

To enable debug logs locally during development, configure python logging. For
example:

```bash
python - <<'PY'
import logging, sys
logging.basicConfig(level=logging.DEBUG)
from pycreative.cli import main
sys.exit(main())
PY
```

Test helper
-----------
A small test-only helper `SkiaGLPresenter._variant_ordering(force_gles_override=None, sniff_override=None)`
returns the ordered list of variant tags (`['es300','150','120']` or
`['150','es300','120']`) so unit tests can assert the presenter's intended
preference without needing a GL context.

Notes for maintainers
---------------------
- Keep diagnostic logging at DEBUG level so it doesn't spam normal runs.
- When adding new shader variants (e.g., older GLES2), update `_variant_ordering`
  and the ADR.
