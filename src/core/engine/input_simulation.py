"""Input simulation helpers extracted from Engine implementation.

These are thin functions that operate on an Engine instance. They mirror the
behaviour previously implemented as instance methods in impl.py but are
extracted to reduce impl.py size. They intentionally avoid heavy top-level
imports and perform lazy imports where appropriate.
"""
from typing import Any, Optional

from .api import SimpleSketchAPI


def _apply_mouse_update(engine: Any, x: Optional[int], y: Optional[int]) -> None:
    """Update pmouse/mouse state on the provided engine instance.

    If x or y is None, preserve the previous coordinate.
    """
    try:
        engine.pmouse_x = int(engine.mouse_x)
    except Exception:
        engine.pmouse_x = 0
    try:
        engine.pmouse_y = int(engine.mouse_y)
    except Exception:
        engine.pmouse_y = 0
    if x is not None:
        try:
            engine.mouse_x = int(x)
        except Exception:
            pass
    if y is not None:
        try:
            engine.mouse_y = int(y)
        except Exception:
            pass


def simulate_mouse_press(
    engine: Any,
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: Optional[str] = None,
    event: Optional[object] = None,
):
    from core.adapters.pyglet_mouse import normalize_event
    ev = normalize_event(event) if event is not None else {}
    ex = ev.get('x', x)
    ey = ev.get('y', y)
    btn = ev.get('button', button)

    engine._ensure_setup()
    _apply_mouse_update(engine, ex, ey)
    engine.mouse_pressed = True
    if btn is not None:
        try:
            engine.mouse_button = str(btn)
        except Exception:
            pass

    handler = getattr(engine.sketch, 'mouse_pressed', None)
    if callable(handler):
        try:
            return handler()
        except TypeError:
            try:
                this = SimpleSketchAPI(engine)
                return engine._call_sketch_method(handler, this)
            except Exception:
                if getattr(engine, '_debug_handler_exceptions', False):
                    raise
                return None
        except Exception:
            if getattr(engine, '_debug_handler_exceptions', False):
                raise
            return None


def simulate_mouse_release(
    engine: Any,
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: Optional[str] = None,
    event: Optional[object] = None,
):
    from core.adapters.pyglet_mouse import normalize_event
    ev = normalize_event(event) if event is not None else {}
    ex = ev.get('x', x)
    ey = ev.get('y', y)
    btn = ev.get('button', button)

    engine._ensure_setup()
    _apply_mouse_update(engine, ex, ey)
    engine.mouse_pressed = False
    if btn is not None:
        try:
            engine.mouse_button = str(btn)
        except Exception:
            pass

    released = getattr(engine.sketch, 'mouse_released', None)
    if callable(released):
        try:
            try:
                released()
            except TypeError:
                this = SimpleSketchAPI(engine)
                engine._call_sketch_method(released, this)
        except Exception:
            pass

    clicked = getattr(engine.sketch, 'mouse_clicked', None)
    if callable(clicked):
        try:
            try:
                clicked()
            except TypeError:
                this = SimpleSketchAPI(engine)
                engine._call_sketch_method(clicked, this)
        except Exception:
            pass


def simulate_mouse_move(
    engine: Any,
    x: Optional[int] = None,
    y: Optional[int] = None,
    event: Optional[object] = None,
):
    from core.adapters.pyglet_mouse import normalize_event
    ev = normalize_event(event) if event is not None else {}
    ex = ev.get('x', x)
    ey = ev.get('y', y)

    engine._ensure_setup()
    _apply_mouse_update(engine, ex, ey)

    moved = getattr(engine.sketch, 'mouse_moved', None)
    if callable(moved):
        try:
            try:
                moved()
            except TypeError:
                this = SimpleSketchAPI(engine)
                engine._call_sketch_method(moved, this)
        except Exception:
            pass


def simulate_mouse_drag(
    engine: Any,
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: Optional[str] = None,
    event: Optional[object] = None,
):
    from core.adapters.pyglet_mouse import normalize_event
    ev = normalize_event(event) if event is not None else {}
    ex = ev.get('x', x)
    ey = ev.get('y', y)
    btn = ev.get('button', button)

    engine._ensure_setup()
    _apply_mouse_update(engine, ex, ey)
    engine.mouse_pressed = True
    if btn is not None:
        try:
            engine.mouse_button = str(btn)
        except Exception:
            pass

    dragged = getattr(engine.sketch, 'mouse_dragged', None)
    if callable(dragged):
        try:
            try:
                dragged()
            except TypeError:
                this = SimpleSketchAPI(engine)
                engine._call_sketch_method(dragged, this)
        except Exception:
            pass


def simulate_mouse_wheel(engine: Any, event_or_count: object):
    # Determine count
    count = None
    try:
        if (
            hasattr(event_or_count, 'get_count')
            and callable(getattr(event_or_count, 'get_count'))
        ):
            _maybe: object = event_or_count.get_count()
            try:
                from typing import Any as _Any
                from typing import cast
                _val: _Any = _maybe
                count = int(cast(int, _val))
            except Exception:
                count = None
    except Exception:
        count = None
    if count is None:
        try:
            from typing import Any as _Any
            _ec: _Any = event_or_count
            count = int(_ec)
        except Exception:
            return None

    engine._ensure_setup()
    handler = getattr(engine.sketch, 'mouse_wheel', None)
    if callable(handler):
        try:
            class _Wheel:
                def __init__(self, c: int):
                    self._c = int(c)

                def get_count(self) -> int:
                    return int(self._c)

            try:
                return handler(_Wheel(count))
            except TypeError:
                this = SimpleSketchAPI(engine)
                return engine._call_sketch_method(handler, this)
        except Exception:
            pass


def simulate_key_press(
    engine: Any,
    key: Optional[str] = None,
    key_code: Optional[str] = None,
    event: Optional[object] = None,
):
    try:
        from core.adapters.pyglet_keyboard import normalize_event
    except Exception:
        def normalize_event(event: Any) -> dict[str, Any]:
            return {}
    ev = normalize_event(event) if event is not None else {}
    k = ev.get('key', key)
    kc = ev.get('key_code', key_code)

    engine._ensure_setup()
    try:
        engine.key = k
    except Exception:
        pass
    try:
        engine.key_code = kc
    except Exception:
        pass
    try:
        engine.key_pressed = True
    except Exception:
        pass

    handler = getattr(engine.sketch, 'key_pressed', None)
    if callable(handler):
        try:
            try:
                return handler()
            except TypeError:
                try:
                    return handler(ev)
                except TypeError:
                    this = SimpleSketchAPI(engine)
                    return engine._call_sketch_method(handler, this)
        except Exception:
            if getattr(engine, '_debug_handler_exceptions', False):
                raise
            return None


def simulate_key_release(
    engine: Any,
    key: Optional[str] = None,
    key_code: Optional[str] = None,
    event: Optional[object] = None,
):
    try:
        from core.adapters.pyglet_keyboard import normalize_event
    except Exception:
        def normalize_event(event: Any) -> dict[str, Any]:
            return {}
    ev = normalize_event(event) if event is not None else {}
    k = ev.get('key', key)
    kc = ev.get('key_code', key_code)

    engine._ensure_setup()
    try:
        engine.key = k
    except Exception:
        pass
    try:
        engine.key_code = kc
    except Exception:
        pass
    try:
        engine.key_pressed = False
    except Exception:
        pass

    handler = getattr(engine.sketch, 'key_released', None)
    if callable(handler):
        try:
            try:
                handler()
            except TypeError:
                try:
                    handler(ev)
                except TypeError:
                    this = SimpleSketchAPI(engine)
                    engine._call_sketch_method(handler, this)
        except Exception:
            if getattr(engine, '_debug_handler_exceptions', False):
                raise
