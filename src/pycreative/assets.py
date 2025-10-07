"""
pycreative.assets: Asset manager for sketches (images, audio, video, etc.)
"""

import os
from typing import Optional, Dict

import pygame


class Assets:
    def __init__(self, sketch_dir: str, debug: bool = False):
        self.sketch_dir = sketch_dir
        # enable verbose debug printing when True
        self.debug = bool(debug)
        # cache maps resolved absolute path -> pygame.Surface
        # Store as an instance attribute so static analyzers understand `self.cache`
        self.cache: Dict[str, pygame.Surface] = {}

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

        if self.debug:
            print(f"[Assets] Debug: sketch_dir={self.sketch_dir}")
        for p in candidates:
            if self.debug:
                print(f"[Assets] Debug: Trying {p}")
            if os.path.exists(p):
                if self.debug:
                    print(f"[Assets] Debug: Found asset at {p}")
                return p

        if self.debug:
            print("[Assets] Debug: Not found in candidate locations")
        return None

    def load_image(self, path: str) -> Optional[pygame.Surface]:
        if self.debug:
            print(f"[Assets] Debug: load_image called with path={path}")
        resolved = self._resolve_path(path)
        if not resolved:
            print(f"[Assets] Error: '{path}' not found in 'data/' or sketch directory: {self.sketch_dir}")
            return None
        if self.debug:
            print(f"[Assets] Debug: Loading image from {resolved}")
        if resolved in self.cache:
            if self.debug:
                print("[Assets] Debug: Returning cached image")
            return self.cache[resolved]
        try:
            img = pygame.image.load(resolved)
            self.cache[resolved] = img
            if self.debug:
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

