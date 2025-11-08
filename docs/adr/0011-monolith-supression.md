# Module Organization Pattern — UNIX-Style Functional Decomposition

## Status: Proposed

Date: 2025-11-08

Context: Python graphics application architecture

## Context

The current Python codebase groups related functions within large monolithic modules.
While this adheres to conventional Python practice, it is leading to increased cognitive load, long file scroll depths, and difficulty isolating functionality for testing and reuse.

Whitespace significance in Python compounds the complexity of maintaining large modules. The application’s domain — real-time graphics and media processing — naturally involves component-style units (renderers, shaders, input handlers, etc.) which are conceptually independent but currently co-located within the same source files.

The author wishes to explore a UNIX-inspired modular architecture: each function or micro-component resides in its own file, exported through a thin shim layer for discovery and composition. This mirrors the modular ergonomics of component frameworks (e.g., React) and enables dynamic composition and reload.

## Decision

Adopt a UNIX-style componentized module structure for the graphics subsystem and other highly composable parts of the application.

### Key principles:

- Each file contains a single focused function or component.
- Each package exposes its contents through an automated __init__.py shim (dynamic import and export).
- High cohesion within directories, low coupling between them.
- Naming conventions reflect functionality, not grouping (load_texture.py, bind_texture.py, release_texture.py rather than texture_utils.py).

## Example structure:

```bash
graphics/
  ├─ shader/
  │   ├─ compile.py
  │   ├─ link.py
  │   ├─ validate.py
  │   └─ __init__.py  # auto-discovers exports
  └─ render/
      ├─ draw_mesh.py
      ├─ draw_texture.py
      └─ __init__.py
```

## Shim example:

```py
# __init__.py
from importlib import import_module
from pathlib import Path

__all__ = []
for path in Path(__file__).parent.glob("*.py"):
    if path.stem == "__init__":
        continue
    mod = import_module(f".{path.stem}", __package__)
    globals()[path.stem] = mod
    __all__.append(path.stem)
```

This enables imports such as:

```py
from graphics.shader import compile, link
compile.run("shader.glsl")
```

## Consequences

### Positive:

- Improved readability through file-level isolation.
- Easier unit testing and hot-reload capabilities.
- Enables plugin-like extensibility for graphics components.
- Reduces merge conflicts and diff noise in large files.
- Aligns with “do one thing well” philosophy (UNIX pattern).

### Negative:

- Increased import overhead and startup time (mitigated via lazy loading).
- Higher file count, potentially overwhelming without strict naming discipline.
- IDE navigation (go-to-definition, search) may require configuration to stay ergonomic.
- Deviates from typical Python convention; potential onboarding friction.

## Alternatives Considered

1. Traditional grouped modules (status quo)
  • Simple import graph, widely understood by Python developers.
  • Unsuitable for dynamic composition and fine-grained reloading.

2. Hybrid component folders (semi-atomic)
  • One directory per logical component, small submodules inside.
  • Still acceptable, but may grow monolithic over time.

## Decision Outcome

Proceed with a gradual migration:
Apply the UNIX-style decomposition or a `Composite` pattern to graphics and rendering modules first, evaluate maintainability and import overhead, and extend pattern to broader system if successful.
Starting with the most fragile and egregious modules such as `skia_gl_present.py` will yield the highest immediate benefit.