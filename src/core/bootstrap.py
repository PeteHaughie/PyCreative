"""Bootstrap helpers to construct Engine and register default adapters.

Keep CLI thin: parse args in CLI, then call bootstrap.build_engine(...) to get
an Engine instance ready to start. This keeps CLI free of wiring details and
centralises defaults for adapters.
"""

from typing import Any


def build_engine(display_adapter: Any = None, draw_adapter: Any = None) -> Any:
    """Return an Engine instance with optional adapters wired.

    The function avoids importing heavy dependencies at module import time.
    """
    # Lazy import of Engine to keep module import lightweight
    try:
        from pycreative.core.engine import Engine  # type: ignore
    except Exception:
        from src.core.engine import Engine  # type: ignore

    engine = Engine()

    # If adapters are provided, register them as APIs so they can perform
    # any wiring with the engine (this mirrors the register_api contract).
    if display_adapter is not None:
        try:
            engine.register_api(display_adapter)
        except Exception:
            pass

    if draw_adapter is not None:
        try:
            engine.register_api(draw_adapter)
        except Exception:
            pass

    return engine
