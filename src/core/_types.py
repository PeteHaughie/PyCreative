from __future__ import annotations

from typing import Any, Optional, Protocol


class APIProtocol(Protocol):
    def get(self, name: str) -> Any: ...


class GraphicsBufferProtocol(Protocol):
    def record(self, op: str, **kwargs: Any) -> Any: ...


class PresenterProtocol(Protocol):
    def present(self, *args: Any, **kwargs: Any) -> Any: ...


class EngineProtocol(Protocol):
    """A conservative protocol describing the engine surface that tests and
    runtime code expect. Keep it minimal and extend when mypy reports
    additional real usages.

    The intent is not to model the full implementation but to teach mypy the
    common dynamic attributes used across the codebase and tests.
    """

    api: APIProtocol
    graphics: Optional[GraphicsBufferProtocol]
    width: int
    height: int

    # common mutables that sketches set/read
    image_mode: Optional[str]
    shape_mode: Optional[str]
    blend_mode: Optional[str]
    fill_alpha: Optional[float]
    stroke_alpha: Optional[float]
    frame_rate: Optional[int]

    # internal helpers used by API wrappers
    _presenter: Any
    _in_draw: Any
    _is_offscreen_graphics: bool
    _sketch_module: Any

    # lifecycle hooks used by SimpleSketchAPI
    def _set_size(self, w: int, h: int) -> None: ...
    def _no_loop(self) -> None: ...
    def _loop(self) -> None: ...
    def _redraw(self) -> None: ...
    def _save_frame(self, path: str) -> None: ...
