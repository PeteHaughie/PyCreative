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
        data_path = os.path.join(self.sketch_dir, "data", *parts)
        sketch_path = os.path.join(self.sketch_dir, *parts)
        print(f"[Assets] Debug: sketch_dir={self.sketch_dir}")
        print(f"[Assets] Debug: Trying data_path={data_path}")
        print(f"[Assets] Debug: Trying sketch_path={sketch_path}")
        if os.path.exists(data_path):
            print("[Assets] Debug: Found in data_path")
            return data_path
        if os.path.exists(sketch_path):
            print("[Assets] Debug: Found in sketch_path")
            return sketch_path
        print("[Assets] Debug: Not found in either location")
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

