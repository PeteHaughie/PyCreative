"""Compatibility shim for the defensive replayer.

Historically `core.io.replay_to_skia` was a large module. It became
corrupted during edits which caused import-time errors. Keep this
module tiny: simply forward the public `replay_to_skia_canvas` symbol
to the small, defensive implementation in `replay_to_skia_impl`.
"""

from __future__ import annotations

from .replay_to_skia_impl import replay_to_skia_canvas

__all__ = ["replay_to_skia_canvas"]
                                        # Still set paint alpha if possible
