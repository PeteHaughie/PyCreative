"""
pycreative.input: Unified event abstraction and dispatch for PyCreative.
"""

import pygame

from dataclasses import dataclass
from typing import Any, Optional


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
    sketch.on_event(e)
