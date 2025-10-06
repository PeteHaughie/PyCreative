"""Small observable-attribute mixin used by examples to react to attribute changes.

This allows subclasses to remain Processing-idiomatic (use plain assignment)
while still reacting to changes (for example updating a radius when mass changes)
without requiring per-attribute property definitions.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Any
import inspect


class Observable:
    """Mixin that lets instances observe attribute assignments.

    Usage:
        self.observe('mass', lambda v: setattr(self, 'radius', v*8))
        self.mass = 10  # observer will run
    """

    def observe(self, name: str, callback: Callable[[Any], None]) -> None:
        """Register callback(new_value) for attribute `name`.

        Callbacks are called after the attribute is assigned.
        """
        if not hasattr(self, "_attr_observers"):
            object.__setattr__(self, "_attr_observers", {})
        obs: Dict[str, List[Callable[[Any], None]]] = getattr(self, "_attr_observers")
        obs.setdefault(name, []).append(callback)

    def unobserve(self, name: str, callback: Callable[[Any], None] | None = None) -> None:
        """Unregister callbacks. If callback is None remove all observers for name."""
        if not hasattr(self, "_attr_observers"):
            return
        obs = getattr(self, "_attr_observers")
        if name not in obs:
            return
        if callback is None:
            obs.pop(name, None)
        else:
            try:
                obs[name].remove(callback)
            except ValueError:
                pass

    def __setattr__(self, name: str, value: Any) -> None:
        # Detect whether the attribute existed before assignment; capture
        # old value only when it did. This avoids calling on_<attr> during
        # initial __init__ assignments.
        existed = hasattr(self, name)
        old = getattr(self, name, None) if existed else None

        # Always perform the assignment first
        object.__setattr__(self, name, value)

        # Then notify explicit observers if any
        obs = getattr(self, "_attr_observers", None)
        if obs:
            cbs = obs.get(name)
            if cbs:
                for cb in list(cbs):
                    try:
                        cb(value)
                    except Exception:
                        # best-effort: swallow observer errors
                        pass

        # Convenience: if the class defines an `on_<attr>` method, call it.
        # Support signatures of either (new_value) or (old_value, new_value).
        method_name = f"on_{name}"
        meth = getattr(self, method_name, None)
        # Only invoke on_<attr> for attributes that existed before assignment
        # so initial __init__ assignments don't trigger them.
        if existed and meth is not None and callable(meth):
            try:
                sig = inspect.signature(meth)
                params = len([
                    p for p in sig.parameters.values()
                    if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                ])
                if params >= 2:
                    # provide (old, new)
                    meth(old, value)
                else:
                    # provide (new,) only
                    meth(value)
            except Exception:
                # best-effort: don't let observer errors propagate
                pass
