from typing import Callable, Dict, Optional


class APIRegistry:
    """Small registry for sketch API functions (rect, line, etc.)."""

    def __init__(self):
        self._map: Dict[str, Callable] = {}

    def register(self, name: str, fn: Callable):
        self._map[name] = fn

    def get(self, name: str) -> Optional[Callable]:
        return self._map.get(name)
