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
    # If the runtime hasn't finished initialization (setup(), display created,
    # pending state applied) we should buffer events so user handlers don't
    # run before their expected attributes exist. Buffer raw pygame events on
    # a per-sketch queue and return early. This is defensive: some sketches
    # or older code may not have the attribute, so use getattr() with a
    # fallback.
    try:
        if not getattr(sketch, "_setup_complete", True):
            # Ensure a queue exists
            q = getattr(sketch, "_pending_event_queue", None)
            if q is None:
                try:
                    sketch._pending_event_queue = []
                    q = sketch._pending_event_queue
                except Exception:
                    # If we cannot create the queue fall back to dropping events
                    q = None
            if q is not None:
                try:
                    q.append(event)
                except Exception:
                    pass
            # Don't dispatch further until the runner flushes the queue.
            return
    except Exception:
        # If anything goes wrong, fall back to normal dispatch below.
        pass

    e = Event.from_pygame(event)
    # Call the general on_event hook first
    try:
        sketch.on_event(e)
    except Exception:
        # don't let user hook errors stop input processing
        pass

    # Default behavior: allow Escape to close the sketch window.
    # This behavior is enabled by default but can be disabled by the sketch
    # via `self.set_escape_closes(False)`.
    try:
        raw = getattr(e, "raw", None)

        # KEY events
        if e.type == "key":
            try:
                sketch.key_code = getattr(e, "key", None)
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

        # MOUSE button events (down/up)
        if e.type == "mouse":
            # Update convenience mouse attributes (best-effort)
            try:
                prev_pos = getattr(sketch, "_mouse_pos_prev", None)
                if prev_pos is None:
                    sketch.pmouse_x = None
                    sketch.pmouse_y = None
                else:
                    sketch.pmouse_x, sketch.pmouse_y = prev_pos

                if getattr(e, "pos", None) is not None:
                    try:
                            pos = e.pos
                            if pos is not None and hasattr(pos, '__iter__'):
                                vals = list(pos)
                                if len(vals) >= 2:
                                    sketch._mouse_x, sketch._mouse_y = vals[0], vals[1]
                                    sketch._mouse_pos_prev = pos
                    except Exception:
                        pass
                else:
                    try:
                        sketch._mouse_x = None
                        sketch._mouse_y = None
                    except Exception:
                        pass

                try:
                    sketch.mouse_button = getattr(e, "button", None)
                except Exception:
                    pass
            except Exception:
                pass

            # Call hooks
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
                pass

        # MOUSE MOTION (move or drag)
        if e.type == "motion":
            try:
                prev_pos = getattr(sketch, "_mouse_pos_prev", None)
                if prev_pos is None:
                    sketch.pmouse_x = None
                    sketch.pmouse_y = None
                else:
                    sketch.pmouse_x, sketch.pmouse_y = prev_pos

                if getattr(e, "pos", None) is not None:
                    try:
                        pos = e.pos
                        if pos is not None and hasattr(pos, '__iter__'):
                            vals = list(pos)
                            if len(vals) >= 2:
                                sketch._mouse_x, sketch._mouse_y = vals[0], vals[1]
                                sketch._mouse_pos_prev = pos
                    except Exception:
                        pass
                else:
                    try:
                        sketch._mouse_x = None
                        sketch._mouse_y = None
                    except Exception:
                        pass

                # call moved vs dragged depending on whether a button is pressed
                if getattr(sketch, "mouse_is_pressed", False):
                    try:
                        sketch.mouse_dragged()
                    except Exception:
                        pass
                else:
                    try:
                        sketch.mouse_moved()
                    except Exception:
                        pass
            except Exception:
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


def dispatch_event_now(sketch, event: Any):
    """
    Immediately dispatch a normalized Event to the sketch without any
    queuing logic. This is intended for internal use when flushing buffered
    events after initialization.
    """
    e = Event.from_pygame(event)
    # Call user on_event first
    try:
        sketch.on_event(e)
    except Exception:
        pass

    try:
        raw = getattr(e, "raw", None)

        if e.type == "key":
            try:
                sketch.key_code = getattr(e, "key", None)
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

            if raw is not None and getattr(raw, "type", None) == pygame.KEYDOWN:
                sketch.key_is_pressed = True
                try:
                    sketch.key_pressed()
                except Exception:
                    pass
            if raw is not None and getattr(raw, "type", None) == pygame.KEYUP:
                sketch.key_is_pressed = False
                try:
                    sketch.key_released()
                except Exception:
                    pass

        if e.type == "mouse":
            try:
                prev_pos = getattr(sketch, "_mouse_pos_prev", None)
                if prev_pos is None:
                    sketch.pmouse_x = None
                    sketch.pmouse_y = None
                else:
                    sketch.pmouse_x, sketch.pmouse_y = prev_pos

                # Guarded extraction of e.pos: ensure it's iterable and has at least two
                # elements before unpacking to avoid TypeErrors and satisfy static
                # type checkers.
                pos_val = getattr(e, "pos", None)
                if pos_val is not None and hasattr(pos_val, "__iter__"):
                    try:
                        vals = list(pos_val)
                        if len(vals) >= 2:
                            sketch._mouse_x, sketch._mouse_y = vals[0], vals[1]
                            sketch._mouse_pos_prev = tuple(vals[0:2])
                    except Exception:
                        pass
                else:
                    sketch._mouse_x = None
                    sketch._mouse_y = None

                sketch.mouse_button = getattr(e, "button", None)
            except Exception:
                pass

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

        if e.type == "motion":
            try:
                prev_pos = getattr(sketch, "_mouse_pos_prev", None)
                if prev_pos is None:
                    sketch.pmouse_x = None
                    sketch.pmouse_y = None
                else:
                    sketch.pmouse_x, sketch.pmouse_y = prev_pos

                pos_val = getattr(e, "pos", None)
                if pos_val is not None and hasattr(pos_val, "__iter__"):
                    try:
                        vals = list(pos_val)
                        if len(vals) >= 2:
                            sketch._mouse_x, sketch._mouse_y = vals[0], vals[1]
                            sketch._mouse_pos_prev = tuple(vals[0:2])
                    except Exception:
                        pass
                else:
                    sketch._mouse_x = None
                    sketch._mouse_y = None

                if getattr(sketch, "mouse_is_pressed", False):
                    try:
                        sketch.mouse_dragged()
                    except Exception:
                        pass
                else:
                    try:
                        sketch.mouse_moved()
                    except Exception:
                        pass
            except Exception:
                pass

        if e.type == "key" and getattr(e, "key", None) == pygame.K_ESCAPE and raw is not None and getattr(raw, "type", None) == pygame.KEYDOWN:
            if getattr(sketch, "_escape_closes", True):
                try:
                    sketch._running = False
                except Exception:
                    pass
    except Exception:
        pass
