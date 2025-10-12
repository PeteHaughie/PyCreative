"""Adapter module for pygame.

All direct imports of `pygame` should live here. This module exposes a small
API to create display surfaces used by the Engine and examples. In test
environments where pygame may not be available, provide a lightweight fallback
object that mimics the parts of the pygame surface API the project uses.
"""
try:
    import pygame  # type: ignore
    _HAS_PYGAME = True
except Exception:  # pragma: no cover - environment-dependent
    pygame = None  # type: ignore
    _HAS_PYGAME = False
from src.core.debug import debug


class _FakeSurface:
    def __init__(self, width: int, height: int):
        self._w = width
        self._h = height

    def get_size(self):
        return (self._w, self._h)

    # Minimal blit stub
    def blit(self, src, dest):
        return None


def create_display_surface(width: int = 640, height: int = 480, use_opengl: bool = False):
    """Create a display surface. Uses pygame when available, otherwise returns a fake surface.

    When `use_opengl=True` and pygame is available, attempt to create the
    display with an OpenGL context. This enables GPU-backed adapters to
    attach Skia GL surfaces to the same context for zero-copy presentation.
    """
    if _HAS_PYGAME and pygame is not None:
        debug(f"Creating pygame display surface (w={width}, h={height}, use_opengl={use_opengl})")
        pygame.display.init()
        flags = 0
        if use_opengl:
            try:
                flags |= pygame.OPENGL
            except Exception:
                # Older pygame versions may not expose OPENGL symbol; fall back
                # to zero flags and let callers handle fallback.
                pass
        surf = pygame.display.set_mode((width, height), flags)
        debug(f"pygame display surface created: {type(surf)}")

        # Extra diagnostics to help determine whether an OpenGL context
        # was actually created (some platforms or pygame builds may ignore
        # the OPENGL flag). Log SDL driver and try to query GL attributes
        # and GL strings via PyOpenGL when available.
        try:
            driver = pygame.display.get_driver()
            debug(f"pygame display driver: {driver}")
        except Exception:
            driver = None

        if use_opengl:
            # Query some GL attributes (best-effort)
            attrs = []
            for name in ("RED_SIZE", "GREEN_SIZE", "BLUE_SIZE", "ALPHA_SIZE", "DEPTH_SIZE", "STENCIL_SIZE"):
                val = None
                try:
                    val = pygame.display.gl_get_attribute(getattr(pygame, f"GL_{name}"))
                except Exception:
                    try:
                        val = pygame.display.gl_get_attribute(getattr(pygame, name))
                    except Exception:
                        val = None
                attrs.append((name, val))
            debug(f"GL attributes: {attrs}")

            # If PyOpenGL is installed, try to query GL strings to confirm
            # a context is active. This is best-effort and will not raise.
            try:
                from OpenGL import GL as _GL  # type: ignore
                try:
                    ver = _GL.glGetString(_GL.GL_VERSION)
                    renderer = _GL.glGetString(_GL.GL_RENDERER)
                    debug(f"PyOpenGL reports GL_VERSION={ver} renderer={renderer}")
                except Exception as exc:
                    debug(f"PyOpenGL present but glGetString failed: {exc}")
            except Exception:
                debug("PyOpenGL not available; cannot query GL_VERSION")

        return surf
    return _FakeSurface(width, height)


def present(surface):
    """Present the current display buffer to the screen.

    For real pygame, this calls display.flip(); for the fake surface it's a no-op.
    """
    if _HAS_PYGAME and pygame is not None:
        try:
            # Update the full display surface to the screen
            debug("pygame.display.flip() called")
            pygame.display.flip()
        except Exception:
            pass
    else:
        # Fake surface: no-op
        return None
