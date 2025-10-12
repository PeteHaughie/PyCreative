"""Compatibility shim: expose `pycreative.core.engine` by delegating to `src.core.engine`.

This allows the console entrypoint and other callers to import `pycreative.core.engine`
in both editable/development layouts (where core lives in `src/core`) and installed
layouts. The shim tries to import the real module and registers it in sys.modules
so subsequent imports resolve to the underlying implementation.
"""
from importlib import import_module
import sys

try:
    real = import_module('src.core.engine')
    # Register the underlying module under the pycreative.core.engine name so
    # `from pycreative.core.engine import Engine` works.
    sys.modules.setdefault(__name__ + '.engine', real)
    # Re-export common symbols
    try:
        Engine = getattr(real, 'Engine')
    except Exception:
        pass
except Exception:
    # If the import fails, leave the package empty; callers will fallback.
    pass
