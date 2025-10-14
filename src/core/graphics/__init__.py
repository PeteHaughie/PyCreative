"""Core graphics helpers and lightweight headless recording buffer.

This package will eventually host the GPU-backed adapters and surfaces.
For now it exposes `GraphicsBuffer` which records drawing commands in
memory for headless tests.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class GraphicsBuffer:
    commands: List[Dict[str, Any]] = field(default_factory=list)

    def clear(self):
        self.commands.clear()

    def record(self, op: str, **kwargs):
        self.commands.append({'op': op, 'args': kwargs})
