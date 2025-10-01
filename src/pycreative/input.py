"""
pycreative.input: Unified event abstraction and dispatch for PyCreative.
"""

from dataclasses import dataclass
from typing import Any, Optional

import pygame


@dataclass
class Event:
    """
    Unified event abstraction for PyCreative.
    """

    type: str
    key: Optional[int] = None
    pos: Optional[tuple] = None
    button: Optional[int] = None
    raw: Any = None

    @staticmethod
    def from_pygame(event: Any) -> "Event":
        # Always set raw=event for all event types
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            return Event(type="key", key=getattr(event, "key", None), raw=event)
        elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
            return Event(
                type="mouse",
                pos=getattr(event, "pos", None),
                button=getattr(event, "button", None),
                raw=event,
            )
        elif event.type == pygame.MOUSEMOTION:
            return Event(type="motion", pos=getattr(event, "pos", None), raw=event)
        else:
            return Event(type=str(event.type), raw=event)


def dispatch_event(sketch, event: Any):
    """
    Dispatch a normalized Event to the sketch's on_event method.
    """
    e = Event.from_pygame(event)
    # print(f"on_event: {event.type} {getattr(event, 'button', None)} {getattr(event, 'raw', None)}")
    sketch.on_event(e)
    # Default behavior: allow Escape to close the sketch window.
    # This behavior is enabled by default but can be disabled by the sketch
    # via `self.set_escape_closes(False)`.
    try:
        raw = getattr(e, "raw", None)
        if e.type == "key" and getattr(e, "key", None) == pygame.K_ESCAPE and raw is not None and getattr(raw, "type", None) == pygame.KEYDOWN:
            if getattr(sketch, "_escape_closes", True):
                # Stop the sketch run loop; teardown will be handled by run().
                try:
                    sketch._running = False
                except Exception:
                    pass
    except Exception:
        # best-effort; don't let input dispatch crash the app
        pass
