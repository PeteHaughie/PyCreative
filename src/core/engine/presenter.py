"""Presenter helpers extracted from Engine implementation.

Small helpers that create a presenter and render recorded commands.
They are intentionally minimal so importing them is cheap in tests.
"""
from typing import Any, Callable, Iterable, Optional
import os


def create_presenter(
    presenter_cls: Any,
    width: int,
    height: int,
    *,
    present_mode=None,
    force_gles: bool = False,
) -> Any:
    """Instantiate a presenter adapter.

    Mirrors the constructor usage that was previously in the engine.
    The helper forwards the optional flags the engine used to pass.
    """
    return presenter_cls(
        width,
        height,
        force_present_mode=present_mode,
        force_gles=force_gles,
    )


def render_and_present(
    presenter: Any,
    cmds: Iterable[dict],
    replay_fn: Optional[Callable[..., None]],
) -> None:
    """Render recorded commands with the presenter and call present().

    Non-fatal errors are swallowed to preserve previous engine behaviour.
    The function attempts a best-effort resize if the presenter exposes
    `width`/`height` attributes, then calls `render_commands` and `present`.
    """
    try:
        # Only resize the presenter if its recorded width/height differ
        # from the presenter's current backing size. Calling resize
        # unconditionally would drop the Skia surface and GL resources
        # each frame which prevents persistence of previous renders.
        if hasattr(presenter, "width") and hasattr(presenter, "height"):
            try:
                req_w = int(getattr(presenter, "width"))
                req_h = int(getattr(presenter, "height"))
                cur_w = getattr(presenter, 'width', None)
                cur_h = getattr(presenter, 'height', None)
                # Some presenters may track backing size separately; if
                # they expose `_surface_size` prefer that for comparison.
                try:
                    cur_surface = getattr(presenter, '_surface_size', None)
                    if cur_surface is not None:
                        cur_w, cur_h = cur_surface[0], cur_surface[1]
                except Exception:
                    pass
                if cur_w is None or cur_h is None or int(cur_w) != req_w or int(cur_h) != req_h:
                    try:
                        presenter.resize(req_w, req_h)
                    except Exception:
                        # Best-effort: ignore resize failures
                        pass
            except Exception:
                # ignore errors determining sizes
                pass

        if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
            try:
                import logging
                logging.getLogger(__name__).debug('render_and_present: presenting %s cmds', len(list(cmds)))
            except Exception:
                pass
        presenter.render_commands(list(cmds), replay_fn)

        if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
            try:
                import logging
                logging.getLogger(__name__).debug('render_and_present: calling present()')
            except Exception:
                pass
        presenter.present()

    except Exception:
        # Guard the helper itself from crashing callers.
        try:
            if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                import traceback
                traceback.print_exc()
        except Exception:
            pass
        return