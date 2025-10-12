"""Bootstrap helpers to construct Engine and register default adapters.

Keep CLI thin: parse args in CLI, then call bootstrap.build_engine(...) to get
an Engine instance ready to start. This keeps CLI free of wiring details and
centralises defaults for adapters.
"""

from typing import Any
from src.core.debug import debug


def build_engine(display_adapter: Any = None, draw_adapter: Any = None, headless: bool = False, use_opengl: bool = False) -> Any:
    """Return an Engine instance with optional adapters wired.

    The function avoids importing heavy dependencies at module import time.
    """
    # Lazy import of Engine to keep module import lightweight. Prefer the
    # local `src.core.engine` in development and test scenarios so tests can
    # monkeypatch it.
    try:
        from src.core.engine import Engine  # type: ignore
    except Exception:
        try:
            from pycreative.core.engine import Engine
        except Exception:
            from src.core.engine import Engine  # type: ignore

    engine = Engine()

    # Store preference so callers (or adapters) can inspect whether the
    # engine intends to run with an OpenGL-backed display/context.
    try:
        engine._use_opengl = bool(use_opengl)
    except Exception:
        pass

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

    # When running headless, register small default adapters so sketches can
    # operate without explicit adapter wiring. These adapters are intentionally
    # tiny and test-friendly: they simply set engine._draw_adapter/_graphics_adapter
    # references and provide no-op drawing methods.
    if headless:
        class HeadlessDrawAdapter:
            def register_api(self, engine):
                engine._draw_adapter = self

            def draw_rect(self, x, y, w, h, color=None, stroke=1):
                # no-op for headless
                return None

            def draw_circle(self, x, y, r, color=None, stroke=1):
                return None

        class HeadlessGraphicsAdapter:
            def register_api(self, engine):
                engine._graphics_adapter = self

        try:
            engine.register_api(HeadlessDrawAdapter())
            engine.register_api(HeadlessGraphicsAdapter())
        except Exception:
            pass
    else:
        # Try to register real adapters when available (pygame/skia). These
        # adapters live under src.core.adapters and encapsulate import-time
        # side-effects so calling code remains import-safe.
        try:
            from src.core.adapters import pygame_adapter as _pg
            # Prefer a GPU-backed skia adapter when available. This adapter
            # will attempt to create GPU-backed Skia surfaces / textures that
            # can be shared with an SDL/OpenGL/Metal context for zero-copy
            # presentation. Fall back to the CPU-backed `skia_adapter` when
            # the GPU path isn't available.
            try:
                from src.core.adapters import skia_gpu_adapter as _skgpu
                sk_adapter = _skgpu
            except Exception as exc:
                # Log why the GPU adapter couldn't be imported — this helps
                # developers diagnose missing skia builds or platform issues.
                try:
                    debug(f"skia_gpu_adapter import failed: {exc}")
                except Exception:
                    pass
                from src.core.adapters import skia_adapter as _sk
                sk_adapter = _sk

            # Create thin API wrappers that register the adapters with the engine
            class PygameAdapterWrapper:
                def register_api(self, engine):
                    engine._display_adapter = _pg

            class SkiaAdapterWrapper:
                def register_api(self, engine):
                    # sk_adapter may be a module (exporting an instance or
                    # a register_api function) or an adapter instance. Handle
                    # both cases so GPU adapter modules that export a
                    # `skia_gpu_adapter` instance or a `register_api` helper
                    # are correctly wired.
                    try:
                        # If the module exposes a register_api function, call it
                        # which allows the module to attach an instance to the
                        # engine in a version-agnostic way.
                        if hasattr(sk_adapter, 'register_api') and callable(getattr(sk_adapter, 'register_api')):
                            try:
                                sk_adapter.register_api(engine)
                                return
                            except Exception:
                                pass

                        # If the module exports a named instance, use it.
                        if hasattr(sk_adapter, 'skia_gpu_adapter'):
                            engine._graphics_adapter = getattr(sk_adapter, 'skia_gpu_adapter')
                            return

                        # Otherwise assume sk_adapter is an instance or module
                        # with callables (legacy path) and set it directly.
                        engine._graphics_adapter = sk_adapter
                    except Exception:
                        engine._graphics_adapter = sk_adapter

            engine.register_api(PygameAdapterWrapper())
            engine.register_api(SkiaAdapterWrapper())
        except Exception:
            # If real adapters aren't available, it's OK — headless fallback
            # covers automated/test environments.
            pass

    return engine
