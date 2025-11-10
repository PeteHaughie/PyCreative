# ADR-00Y: Error Handling Policy — Structured, Centralized, and Declarative

Status: Proposed
Date: 2025-11-08
Context: Python graphics application architecture

## Context

The current codebase exhibits significant try/except proliferation.
While defensive programming ensures runtime stability, it also introduces verbosity, cognitive overhead, and inconsistent error semantics across modules.

Python’s “Easier to Ask Forgiveness than Permission” (EAFP) idiom encourages exception-driven control flow. However, in large applications — particularly graphics, media, and async systems — scattering exception blocks leads to:

- Unclear error propagation paths,
- Redundant logging and handling, and
- Difficult maintenance or testing due to inconsistent recovery logic.

The goal is to define a structured and centralized error-handling policy that maintains safety without defensive bloat, preserving both clarity and control.

## Decision

Adopt a centralized and layered error-handling architecture that defines where and how exceptions are handled, emphasizing clear contracts, composability, and domain-specific semantics.

## Principles

- Handle exceptions once per layer — errors are caught and re-raised or translated at clear subsystem boundaries.
- Define domain-specific exceptions to replace generic ones (RenderError, ShaderCompileError, TextureLoadError, etc.).
- Use context managers and decorators for recurring safety patterns (e.g. cleanup, logging, resource management).
- Use Result-like return objects (e.g. Ok / Err) where predictable error flow is preferable to exceptions.
- Pre-validate inputs (via typing, asserts, or dataclass validation) to prevent recoverable exceptions entirely.
- Centralize fatal exception handling in the top-level application loop or orchestration layer.

## Example Implementation

1. Centralized Handling in the Main Loop

```py
def run_loop():
    try:
        while app.running:
            update()
            draw()
    except RenderError as e:
        log.error(f"Render failure: {e}")
    except Exception as e:
        handle_critical_error(e)
```

2. Layered Exception Translation

```py
# graphics/shader.py
class ShaderCompileError(Exception): pass

def compile_shader(src):
    try:
        return gpu.compile(src)
    except GPUError as e:
        raise ShaderCompileError(str(e))
```

3. Context Manager for Resource Safety

```py
from contextlib import contextmanager

@contextmanager
def safe_texture(path):
    tex = load_texture(path)
    try:
        yield tex
    finally:
        tex.release()
```

4. Functional Result Pattern (optional)

```py
@dataclass
class Ok: value: object
@dataclass
class Err: error: str

def load_texture(path) -> Ok | Err:
    if not Path(path).exists():
        return Err("missing file")
    return Ok(Texture(path))
```

## Consequences

### Positive:

- Reduced visual noise from repetitive try/except blocks.
- Consistent and predictable error behavior across modules.
- Easier debugging — domain-specific error names clarify origin.
- Safe, declarative cleanup using contextlib or decorators.
- Encourages clear contracts between modules.

### Negative:

- Requires some up-front refactoring and classifying of exception types.
- Slightly less explicit local handling (relies on layered propagation).
- Functional “Result” style introduces minor boilerplate when used widely.

## Alternatives Considered

Local try/except everywhere (status quo)

- High safety, poor maintainability.
- Strict type checking and validation only
- Prevents most errors but doesn’t handle runtime edge cases.
- Framework-level error middleware (async apps)
- Viable in web or asyncio contexts but heavy for graphics applications.

## Decision Outcome

Proceed with layered, centralized error handling.

## Immediate focus:

- Introduce domain exception classes under errors/.
- Replace local try/except with structured boundaries at renderer, I/O, and orchestration layers.
- Introduce helper decorators and context managers for common safety patterns.
- Evaluate Result-style returns for I/O-heavy components after initial migration.