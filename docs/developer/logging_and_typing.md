# Logging and Typing rollout

This document captures the proposed plan for adding structured logging and expanding typing hints across the codebase. It is intentionally lightweight so contributors can follow a consistent pattern when adding instrumentation or type annotations.

Goals
 - Add structured, contextual logging to key runtime components (Engine, GraphicsBuffer, presenters, adapters).
 - Use module-level loggers (via `logging.getLogger(__name__)`) and include machine-readable fields where helpful: `seq`, `frame`, `op`, `sketch`, `presenter`.
 - Standardize log levels: DEBUG for verbose internals, INFO for important lifecycle transitions (engine start/stop, presenter attach), WARNING for recoverable issues, ERROR for unrecoverable errors.
 - Incrementally add mypy-friendly type hints to `src/` modules with a target of `mypy src` passing on CI.

Guidelines
 - Logger creation: each module should create a logger at the top:

```py
import logging
logger = logging.getLogger(__name__)
```

- Use structured logging-friendly message text and include context via kwargs when possible. Example:

```py
logger.debug('recorded command', extra={'op': op, 'seq': seq, 'frame': frame})
```

- Prefer `logger.exception(...)` inside except blocks to capture tracebacks.

- Avoid printing to stdout/stderr for diagnostic messages — use the logger.

Typing
 - Start by adding type hints to core modules: `core/engine`, `core/graphics`, `core/shape`, and `core/color`.
 - Use `from __future__ import annotations` to avoid runtime import cycles and simplify forward references.
 - Annotate public API functions first (inputs/outputs). For private/internal functions prefer gradual typing.
 - Keep mypy configuration in `pyproject.toml` aligned with the project's tolerance for third-party stubs (e.g., allow untyped imports where appropriate).

Rollout plan (phased)
 1. Implement module-level loggers in `core/engine/impl.py`, `core/graphics/__init__.py`, and `core/adapters/*`. Add a few key DEBUG/INFO logs to capture lifecycle events and recorded command emission.
 2. Run tests and adjust log messages to be non-verbose by default. Add simple CI target that ensures logging calls don't introduce new dependencies or side-effects.
 3. Add types to the Engine and GraphicsBuffer public APIs; aim to get `mypy src/core/engine.py src/core/graphics.py` to pass.
 4. Expand to presenters and adapters, adding logs for replay and draw operations.

Next steps (short-term)
 - Add logger instantiation in `src/core/graphics/__init__.py` and `src/core/engine/impl.py` and add a handful of `logger.debug()` calls to record when commands are recorded and when frames start/end.
 - Add the `Logging & typing rollout` task to the project todo (done).

Notes
 - Keep log volume reasonable; tests expect deterministic buffers and should not rely on logs for behavior. Ensure logs remain optional and configurable via environment or application-level configuration.

If you'd like, I can implement the short-term step (add module-level loggers and a few debug/info logs to Engine and GraphicsBuffer) and run tests to ensure nothing breaks. Which would you like me to do next?
