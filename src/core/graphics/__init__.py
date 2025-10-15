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
    _seq: int = 0

    def clear(self):
        self.commands.clear()

    def record(self, op: str, **kwargs):
        self._seq += 1
        meta = {'seq': self._seq}
        self.commands.append({'op': op, 'args': kwargs, 'meta': meta})
