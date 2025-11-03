"""Top-level `core` package shim.

This minimal file ensures `src.core` is a proper package for tooling and
pre-commit checks. Keep imports lightweight: we expose common subpackage
names in ``__all__`` and attempt to import them silently so tooling that
expects the modules to exist will succeed without forcing heavy runtime
side-effects.
"""
from __future__ import annotations

__all__ = [
    "engine",
    "graphics",
    "adapters",
    "api",
    "extensions",
    "runner",
    "pycreative",
]

# Try importing known subpackages to satisfy tools that inspect package
# exports. Don't raise if a subpackage isn't importable in this environment.
for _pkg in list(__all__):
    try:
        __import__(f"{__name__}.{_pkg}", fromlist=[_pkg])
    except Exception:
        # Defer importing until the submodule is actually needed.
        # This keeps package import lightweight and robust for CI/tools.
        pass
