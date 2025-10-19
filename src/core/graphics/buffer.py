"""Graphics recording buffer for headless tests.

This module holds the in-memory `GraphicsBuffer` used by the Engine to
record draw commands for headless rendering and testing.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class GraphicsBuffer:
    commands: List[Dict[str, Any]] = field(default_factory=list)
    _seq: int = 0

    def clear(self) -> None:
        self.commands.clear()

    def record(self, op: str, **kwargs) -> None:
        self._seq += 1
        meta = {'seq': self._seq}
        self.commands.append({'op': op, 'args': kwargs, 'meta': meta})
