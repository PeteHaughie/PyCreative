"""Thin facade for the Engine implementation.

Keep the public surface tiny. Implementations live in
`src.core.engine_impl`. Guidelines:

- Keep implementation files < 400 lines where possible.
- Expose small, atomic methods that are easy to unit-test.
- Delegate rendering, GPU, and heavy work to adapters under
  `src.core.adapters`.

This module simply re-exports the Engine class from the implementation
module so callers import `src.core.engine.Engine` without surprising
import-time side-effects.
"""

from src.core.engine import Engine  # re-export the compact implementation

__all__ = ["Engine"]
