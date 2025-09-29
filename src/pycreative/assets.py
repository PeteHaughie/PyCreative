"""
pycreative.assets: Asset manager for sketches (images, audio, video, etc.)
"""

import os
from typing import Optional

import pygame


class Assets:
    def __init__(self, sketch_dir: str):
        self.sketch_dir = sketch_dir
        self.cache = {}

    def _resolve_path(self, path: str) -> Optional[str]:
        parts = path.replace("\\", "/").split("/")
        candidates = []
        # Primary: sketch_dir/data/<path>
        candidates.append(os.path.join(self.sketch_dir, "data", *parts))
        # Secondary: sketch_dir/<path>
        candidates.append(os.path.join(self.sketch_dir, *parts))
        # Common alternate locations to support running examples from repo root
        candidates.append(os.path.join(self.sketch_dir, "examples", "data", *parts))
        candidates.append(os.path.join(self.sketch_dir, "examples", *parts))

        print(f"[Assets] Debug: sketch_dir={self.sketch_dir}")
        for p in candidates:
            print(f"[Assets] Debug: Trying {p}")
            if os.path.exists(p):
                print(f"[Assets] Debug: Found asset at {p}")
                return p

        print("[Assets] Debug: Not found in candidate locations")
        return None

    def load_image(self, path: str) -> Optional[pygame.Surface]:
        print(f"[Assets] Debug: load_image called with path={path}")
        resolved = self._resolve_path(path)
        if not resolved:
            print(f"[Assets] Error: '{path}' not found in 'data/' or sketch directory: {self.sketch_dir}")
            return None
        print(f"[Assets] Debug: Loading image from {resolved}")
        if resolved in self.cache:
            print("[Assets] Debug: Returning cached image")
            return self.cache[resolved]
        try:
            img = pygame.image.load(resolved)
            self.cache[resolved] = img
            print("[Assets] Debug: Image loaded successfully")
            return img
        except Exception as e:
            print(f"[Assets] Error loading image '{resolved}': {e}")
            return None

    def load_media(self, path: str) -> Optional[str]:
        """Return the resolved file path for audio/video assets."""
        resolved = self._resolve_path(path)
        if not resolved:
            print(
                f"[Assets] Error: '{path}' not found in 'data/' or sketch directory: {self.sketch_dir}"
            )
            return None
        return resolved

