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
        # Update sketch key convenience state for key events
        if e.type == "key":
            try:
                sketch.key_code = getattr(e, "key", None)
                # readable name if possible
                if sketch.key_code is not None:
                    try:
                        sketch.key = pygame.key.name(sketch.key_code)
                    except Exception:
                        sketch.key = None
                else:
                    sketch.key = None
            except Exception:
                sketch.key = None
                sketch.key_code = None

            # KEYDOWN
            if raw is not None and getattr(raw, "type", None) == pygame.KEYDOWN:
                sketch.key_is_pressed = True
                # call hook if present
                try:
                    sketch.key_pressed()
                except Exception:
                    pass
            # KEYUP
            if raw is not None and getattr(raw, "type", None) == pygame.KEYUP:
                sketch.key_is_pressed = False
                try:
                    sketch.key_released()
                except Exception:
                    pass

        # MOUSE events: set convenience properties and call mouse hooks
        if e.type == "mouse":
            # best-effort attribute updates, but ensure hooks are still called
            # (don't let property/setter errors prevent hook invocation)
            try:
                prev_pos = getattr(sketch, "_mouse_pos_prev", None)
                if prev_pos is None:
                    sketch.pmouse_x = None
                    sketch.pmouse_y = None
                else:
                    sketch.pmouse_x, sketch.pmouse_y = prev_pos

                # store current pos on internal attrs to avoid clobbering read-only properties
                if getattr(e, "pos", None) is not None:
                    try:
                        sketch._mouse_x, sketch._mouse_y = e.pos
                        sketch._mouse_pos_prev = e.pos
                    except Exception:
                        # ignore failures to set internal attrs
                        pass
                else:
                    try:
                        sketch._mouse_x = None
                        sketch._mouse_y = None
                    except Exception:
                        pass

                # public mouse_button and is_pressed are safe to set
                try:
                    sketch.mouse_button = getattr(e, "button", None)
                except Exception:
                    pass
            except Exception:
                # ignore attr update errors
                pass

            # Call hooks based on the raw pygame event type (fire-and-forget)
            try:
                if raw is not None and getattr(raw, "type", None) == pygame.MOUSEBUTTONDOWN:
                    try:
                        sketch.mouse_is_pressed = True
                    except Exception:
                        pass
                    try:
                        sketch.mouse_pressed()
                    except Exception:
                        pass
                if raw is not None and getattr(raw, "type", None) == pygame.MOUSEBUTTONUP:
                    try:
                        sketch.mouse_is_pressed = False
                    except Exception:
                        pass
                    try:
                        sketch.mouse_released()
                    except Exception:
                        pass
            except Exception:
                # don't allow hook exceptions to crash dispatch
                pass

        # Allow Escape to close the sketch window on keydown by default
        if e.type == "key" and getattr(e, "key", None) == pygame.K_ESCAPE and raw is not None and getattr(raw, "type", None) == pygame.KEYDOWN:
            if getattr(sketch, "_escape_closes", True):
                try:
                    sketch._running = False
                except Exception:
                    pass
    except Exception:
        # best-effort; don't let input dispatch crash the app
        pass
