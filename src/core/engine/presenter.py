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
    window: Any | None = None,
) -> Any:
    """Instantiate a presenter adapter.

    Mirrors the constructor usage that was previously in the engine.
    The helper forwards the optional flags the engine used to pass.
    """
    # Pass the optional window through so presenters can query the
    # framebuffer backing size / pixel ratio when creating GL resources.
    try:
        return presenter_cls(
            width,
            height,
            force_present_mode=present_mode,
            force_gles=force_gles,
            window=window,
        )
    except TypeError:
        # Backwards-compatible: if the presenter doesn't accept `window`,
        # fall back to the older constructor signature.
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
                # Ask GL for the current drawable size (viewport) and prefer
                # that when deciding to resize. This avoids creating an FBO
                # at logical sizes when the framebuffer uses device pixels
                # (HiDPI / Retina displays).
                try:
                    from pyglet import gl
                    vp = (gl.GLint * 4)()
                    try:
                        gl.glGetIntegerv(gl.GL_VIEWPORT, vp)
                        vp_w = int(vp[2])
                        vp_h = int(vp[3])
                        if vp_w and vp_h:
                            req_w, req_h = int(vp_w), int(vp_h)
                    except Exception:
                        pass
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

        # Call present once. If present() returns True it indicates the
        # presenter detected that the drawable (viewport) size changed and
        # resized itself. In that case we should re-render the recorded
        # commands so the Skia surface/texture are created at the new
        # device-pixel size and then present again. Limit to one extra
        # re-render to avoid infinite loops.
        try:
            # Debug: report what `presenter.present` attribute is bound to
            if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                try:
                    import logging
                    pres_attr = getattr(presenter, 'present', None)
                    try:
                        qual = getattr(pres_attr, '__qualname__', None)
                    except Exception:
                        qual = None
                    try:
                        mod = getattr(pres_attr, '__module__', None)
                    except Exception:
                        mod = None
                    logging.getLogger(__name__).debug('render_and_present: presenter.present attr=%r module=%r qualname=%r', pres_attr, mod, qual)
                    try:
                        print(f'RENDER_AND_PRESENT: presenter.present={pres_attr} module={mod} qualname={qual}')
                    except Exception:
                        pass
                except Exception:
                    pass
            did_resize = presenter.present()
        except Exception:
            did_resize = False

        if did_resize:
            try:
                # Re-render at the new size and present again
                presenter.render_commands(list(cmds), replay_fn)
                try:
                    presenter.present()
                except Exception:
                    pass
            except Exception:
                # Best-effort: ignore render failures on the second pass
                pass

    except Exception:
        # Guard the helper itself from crashing callers.
        try:
            if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                import traceback
                traceback.print_exc()
        except Exception:
            pass
        return