from __future__ import annotations

from typing import Any, Optional, Protocol


class APIProtocol(Protocol):
    def get(self, name: str) -> Any: ...
    def register(self, name: str, fn: Any) -> None: ...


class GraphicsBufferProtocol(Protocol):
    def record(self, op: str, **kwargs: Any) -> Any: ...
    # The recorded commands list is inspected by the presenter/loop code.
    commands: list[Any]


class PresenterProtocol(Protocol):
    def present(self, *args: Any, **kwargs: Any) -> Any: ...
    def resize(self, w: int, h: int) -> None: ...
    def ensure_resources(self) -> None: ...
    def teardown(self) -> None: ...
    # optional attributes some presenters expose
    replay_fn: Any
    fbo_id: Any
    _setup_background_color: Any


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
    # common drawing state stored on the engine
    fill_color: Any
    stroke_color: Any
    stroke_weight: Any
    # optional stroke style attributes
    stroke_cap: Any
    stroke_join: Any

    # internal helpers used by API wrappers
    _presenter: Any
    _in_draw: Any
    _is_offscreen_graphics: bool
    _sketch_module: Any
    # internal state used by the window loop and transforms helpers
    _matrix_stack: Any
    _window: Any
    _pending_save_frames: Any
    _setup_bg_applied: Any
    _default_bg_applied: Any
    _default_bg_cleared: Any
    _apply_mouse_update: Any
    sketch: Any
    _call_sketch_method: Any
    mouse_pressed: Any
    mouse_button: Any
    key: Any
    key_code: Any
    key_pressed: Any
    _setup_background: Any
    _setup_done: Any
    _ignore_no_loop: Any
    looping: Any
    _no_loop_drawn: Any
    _frames_left: Any
    _verbose: Any
    # lifecycle helpers
    def step_frame(self) -> None: ...

    # lifecycle hooks used by SimpleSketchAPI
    def _set_size(self, w: int, h: int) -> None: ...
    def _no_loop(self) -> None: ...
    def _loop(self) -> None: ...
    def _redraw(self) -> None: ...
    def _save_frame(self, path: str) -> None: ...

    # common transform helpers used by SimpleSketchAPI
    def translate(self, x: float, y: float, z: Any = ...) -> Any: ...
    def rotate(self, angle: float) -> Any: ...
    def scale(self, sx: float, sy: Any = ..., sz: Any = ...) -> Any: ...
    def push_matrix(self) -> Any: ...
    def pop_matrix(self) -> Any: ...
    def shear_x(self, angle: float) -> Any: ...
    def shear_y(self, angle: float) -> Any: ...
    def reset_matrix(self) -> Any: ...
    def apply_matrix(self, *args: Any) -> Any: ...
