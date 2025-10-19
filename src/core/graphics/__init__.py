"""Core graphics helpers and lightweight headless recording buffer.

Keep this package thin: implementations live in sibling modules.
"""
from __future__ import annotations

# Re-export submodules
from . import buffer

__all__ = [
    'buffer',
    'GraphicsBuffer',
]

# Convenience re-export of the main class
from .buffer import GraphicsBuffer
