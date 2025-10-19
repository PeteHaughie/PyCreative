"""Compatibility shim: re-export APIRegistry from the new api package.

This module previously contained the APIRegistry implementation directly
but was moved into ``core.engine.api.registry`` during the package
reorganization. Keep this shim to preserve the old import path while
consumers migrate.
"""

from .api.registry import APIRegistry

__all__ = ["APIRegistry"]
