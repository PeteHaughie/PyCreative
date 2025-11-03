"""Small typing shims re-exported for modules that live under the
`pycreative` package so mypy sees a single package-root for shared types.

This module re-exports the conservative EngineProtocol defined under
`core._types` to avoid duplicate-module resolution issues when mypy
analyses both `pycreative.*` and `core.*` packages in the same run.
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    # For static typing, use the canonical protocol defined under core
    from core._types import EngineProtocol
else:
    # Runtime fallback when `core._types` isn't importable (tests/runtime
    # may run with different import paths).
    class EngineProtocol:
        api: Any
        graphics: Any
        width: int
        height: int
        image_mode: Any
        shape_mode: Any
        blend_mode: Any
        fill_alpha: Any
        stroke_alpha: Any
        frame_rate: Any
        _presenter: Any
        _in_draw: Any
        _is_offscreen_graphics: Any
        _sketch_module: Any

        def _set_size(self, w: int, h: int) -> None: ...
        def _no_loop(self) -> None: ...
        def _loop(self) -> None: ...
        def _redraw(self) -> None: ...
        def _save_frame(self, path: str) -> None: ...

__all__ = ["EngineProtocol"]
