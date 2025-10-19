"""Presenter helpers extracted from Engine implementation.

Small helpers that create a presenter and render recorded commands.
They are intentionally minimal so importing them is cheap in tests.
"""
from typing import Any, Callable, Iterable, Optional


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
        if hasattr(presenter, "width") and hasattr(presenter, "height"):
            try:
                presenter.resize(getattr(presenter, "width"), getattr(presenter, "height"))
            except Exception:
                # Best-effort: ignore resize failures
                pass

        try:
            presenter.render_commands(list(cmds), replay_fn)
        except Exception:
            # Non-fatal: fall through to present attempt
            pass

        try:
            presenter.present()
        except Exception:
            # Non-fatal: ignore present errors
            pass

    except Exception:
        # Guard the helper itself from crashing callers.
        return