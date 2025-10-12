# GPU Integration Guide

This document explains how to run PyCreative with a GPU-backed Skia renderer (OpenGL), what dependencies are required, and how to run the integration test.

Prerequisites
- Python 3.11
- pygame built with OpenGL support (standard pygame + SDL2 with GL on most platforms)
- skia-python built with the OpenGL backend enabled
- PyOpenGL (optional; used by the adapter's GL path)
- numpy (optional; used by the CPU fallback path for unpremultiplying)

Install suggestions (macOS example)

```bash
# Create and activate venv
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
# Install pygame (ensure SDL2 with OpenGL is available on your system)
pip install pygame
# skia-python with GPU support must be built; see skia-python docs.
# On macOS you may prefer a Metal-backed skia build; this repository currently
# implements an OpenGL adapter. If you need Metal, add a skia_metal_adapter later.
pip install PyOpenGL numpy
```

Running a GPU-enabled sketch

1. Ensure you have a skia-python build with OpenGL support and that `import skia` works.
2. Run the CLI with the `--use-opengl` flag:

```bash
pycreative examples/sketch_example.py --use-opengl
```

This will attempt to create a pygame display with an OpenGL context and then ask the GPU adapter to create a Skia GL-backed surface.

Integration test

The repository includes a gated integration test `tests/integration/test_gpu_path.py` which is skipped by default. To run it locally, set the `SKIA_GPU=1` environment variable and ensure the prerequisites above are installed.

```bash
SKIA_GPU=1 pytest tests/integration/test_gpu_path.py -q
```

Notes

- The OpenGL adapter is conservative and feature-detects available skia-python APIs. Exact APIs may vary by skia-python version; if the integration fails locally, examine the skia-python docs or let me adapt the adapter to the specific API on your machine.
- Metal/Vulkan adapters can be added later using the same adapter interface (`create_gpu_surface`, `present`).
