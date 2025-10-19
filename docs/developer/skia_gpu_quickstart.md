# Skia GPU Quickstart (local developer guide)

This document records the steps used during an exploratory run that renders
using skia-python into an OpenGL FBO and displays the result in a pyglet
window. It includes commands, troubleshooting tips, and the snapshot path.

Prerequisites
-------------
- macOS or Linux with GPU drivers
- Python 3.11 (project targets >=3.11)
- The project's virtualenv in the repository root (created by the developer)

Local reproduction steps
------------------------
1. Activate the project's venv:

    source venv/bin/activate

2. Install runtime dependencies (only needed for local GPU demo):

    pip install --upgrade pip setuptools wheel
    pip install skia-python pyglet pillow numpy

3. Run the demo script (performed interactively during development):

    python - <<'PY'
    # (Script used during exploration: creates an FBO, renders with Skia,
    #  reads pixels back and writes skia_readback.png, displays via pyglet.)
    PY

4. The snapshot was written to the repository root as `skia_readback.png`.

Troubleshooting notes
---------------------
- If `skia-python` fails to import, verify you installed the wheel for your
  platform and Python version. On macOS Apple silicon, choose wheels built
  for arm64 / macOS 11+. If CI must run on Linux, ensure CI runners have
  compatible wheels or provide a documented CPU fallback.
- Some skia builds returned `encodeToData()` as None. We used `glReadPixels`
  from the bound FBO as a robust fallback to obtain pixel data.
- Quick open/close of pyglet windows on macOS can produce benign objc/ctypes
  warnings; they're expected in short-run tests but can be suppressed by
  longer-lived windows or graceful teardown.

