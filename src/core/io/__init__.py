"""IO helpers package for core.

Keep lightweight to avoid importing heavy dependencies at package import
time. Use module-level shims to expose public APIs.
"""
from __future__ import annotations

# Re-export submodules; keep this file intentionally light so importing
# `core.io` doesn't pull in heavy optional dependencies like PIL or skia.
from . import replayer
# The legacy `replay_to_skia` module had issues; prefer the defensive
# implementation in `replay_to_skia_impl` and expose it under the old
# name so callers importing `core.io.replay_to_skia` continue to work.
from . import replay_to_skia_impl as replay_to_skia
from . import skia_replayer
from . import snapshot

__all__ = [
	'replayer',
	'replay_to_skia',
	'skia_replayer',
	'snapshot',
]
