"""
pycreative.assets: Asset manager for sketches (images, audio, video, etc.)
"""

import os
from typing import Optional, Dict, Any

import pygame


class Assets:
    # Cache mapping (path or (path,size)) -> loaded asset
    cache: Dict[Any, Any]
    def __init__(self, sketch_dir: str, debug: bool = False):
        self.sketch_dir = sketch_dir
        # enable verbose debug printing when True
        self.debug = bool(debug)
        # cache maps resolved absolute path or (path,size) tuples -> asset
        # (pygame.Surface, pygame.font.Font, PShape, or filepath). Store as an
        # instance attribute so static analyzers understand `self.cache`.
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

    def load_shape(self, path: str):
        """Load a vector shape (SVG/OBJ) and return a PShape-like object or None."""
        if self.debug:
            print(f"[Assets] Debug: load_shape called with path={path}")
        resolved = self._resolve_path(path)
        if not resolved:
            print(f"[Assets] Error: '{path}' not found in 'data/' or sketch directory: {self.sketch_dir}")
            return None
        if resolved in self.cache:
            if self.debug:
                print("[Assets] Debug: Returning cached shape")
            return self.cache[resolved]
        try:
            # Import here to avoid a hard dependency if unused
            from .shape import load_shape_from_file

            shp = load_shape_from_file(resolved)
            if shp is None:
                if self.debug:
                    print(f"[Assets] Debug: load_shape returned None for {resolved}")
                return None
            self.cache[resolved] = shp
            if self.debug:
                print("[Assets] Debug: Shape loaded successfully")
            return shp
        except Exception as e:
            print(f"[Assets] Error loading shape '{resolved}': {e}")
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

    def load_font(self, path: str, size: int = 24):
        """Resolve a font file path in the sketch and return a pygame.font.Font instance or None.

        `path` may be relative to the sketch's `data/` folder or a direct file path.
        """
        # Try to find a system-installed font first (by family/name). This
        # lets users pass a font name like "arial" and get a system-provided
        # TTF if installed. Use pygame.font.match_font which returns an
        # absolute path to a matching font file or None.
        try:
            try:
                sys_path = pygame.font.match_font(path)
            except Exception:
                sys_path = None
            # Ignore font collection files (.ttc) because FreeType/SDL may
            # select an unpredictable face from the collection which can
            # look unlike the requested family. Treat .ttc as no-match so
            # callers can fall back to local assets or explicit TTF names.
            try:
                if isinstance(sys_path, str) and sys_path.lower().endswith('.ttc'):
                    if self.debug:
                        print(f"[Assets] Debug: Ignoring matched TTC font path: {sys_path}")
                    sys_path = None
            except Exception:
                pass
            # If match_font returned nothing or a TTC was ignored, attempt a
            # smarter search through available system font family names to
            # prefer a non-.ttc (TTF/OTF) match. This helps on macOS where
            # 'courier' may resolve to a TTC but 'courier new' resolves to a
            # TTF.
            if not sys_path:
                try:
                    sys_fonts = pygame.font.get_fonts() or []
                except Exception:
                    sys_fonts = []
                # Normalized requested name for loose matching
                try:
                    req_norm = str(path).lower().replace(' ', '')
                except Exception:
                    req_norm = ''
                # Prepare ordered candidates that are likely to succeed
                candidates = []
                # common explicit variant
                if req_norm:
                    candidates.append(req_norm + 'new')
                    candidates.append(''.join(req_norm.split()))
                # then any family that contains the requested substring
                for fam in sys_fonts:
                    try:
                        fam_norm = fam.lower().replace(' ', '')
                    except Exception:
                        fam_norm = fam
                    if req_norm and (req_norm in fam_norm or fam_norm in req_norm):
                        candidates.append(fam)
                # Finally try all system fonts (best-effort)
                candidates.extend(sys_fonts)
                # Try each candidate via match_font and pick the first non-TTC
                chosen = None
                for cand in candidates:
                    try:
                        cand_path = pygame.font.match_font(cand)
                    except Exception:
                        cand_path = None
                    if not cand_path:
                        continue
                    try:
                        if cand_path.lower().endswith('.ttc'):
                            if self.debug:
                                print(f"[Assets] Debug: Skipping TTC candidate {cand} -> {cand_path}")
                            continue
                    except Exception:
                        pass
                    # Found a usable non-TTC system font file
                    chosen = cand_path
                    if self.debug:
                        print(f"[Assets] Debug: Using system font candidate {cand} -> {chosen}")
                    break
                if chosen:
                    sys_path = chosen
            if sys_path:
                key = (sys_path, int(size))
                if key in self.cache:
                    return self.cache[key]
                try:
                    font = pygame.font.Font(sys_path, int(size))
                    self.cache[key] = font
                    return font
                except Exception as e:
                    if self.debug:
                        print(f"[Assets] Debug: match_font returned {sys_path} but loading failed: {e}")
                    # fall through to try resolving local path
        except Exception:
            # If pygame isn't available or something failed, proceed to local lookup
            pass

        # Fallback: attempt to resolve as a local file relative to the sketch
        resolved = self._resolve_path(path)
        if not resolved:
            if self.debug:
                print(f"[Assets] Debug: font '{path}' not found locally in sketch data or examples")
            print(f"[Assets] Error: font '{path}' not found in 'data/' or sketch directory: {self.sketch_dir}")
            return None
        key = (resolved, int(size))
        if key in self.cache:
            return self.cache[key]
        try:
            font = pygame.font.Font(resolved, int(size))
            # cache by resolved path + size
            self.cache[key] = font
            return font
        except Exception as e:
            print(f"[Assets] Error loading font '{resolved}': {e}")
            return None

    def list_fonts(self, include_paths: bool = False) -> list:
        """Return a list of available fonts.

        The returned list places fonts found under the sketch's data/examples
        directories first (local bundled fonts), followed by system-installed
        font family names discovered via pygame.font.get_fonts().

        When `include_paths` is True the function returns a list of tuples
        (name, path) for local fonts and (name, None) for system families.
        """
        local_fonts: dict[str, str] = {}
        # Candidate directories to search for bundled fonts
        candidates = [
            os.path.join(self.sketch_dir, "data"),
            os.path.join(self.sketch_dir),
            os.path.join(self.sketch_dir, "examples", "data"),
            os.path.join(self.sketch_dir, "examples"),
        ]
        # Prefer individual font files; ignore font collections (.ttc)
        exts = {".ttf", ".otf"}
        for base in candidates:
            try:
                if not os.path.isdir(base):
                    continue
                for entry in os.listdir(base):
                    try:
                        lower = entry.lower()
                        name, ext = os.path.splitext(lower)
                        if ext in exts:
                            full = os.path.join(base, entry)
                            # Use display name without extension; prefer first-found
                            if name not in local_fonts:
                                local_fonts[name] = full
                    except Exception:
                        continue
            except Exception:
                continue

        results: list = []
        # Add local fonts first
        for name, path in local_fonts.items():
            if include_paths:
                results.append((name, path))
            else:
                results.append(name)

        # Then append system font family names
        try:
            import pygame as _pygame

            try:
                sys_fonts = _pygame.font.get_fonts() or []
            except Exception:
                sys_fonts = []
        except Exception:
            sys_fonts = []

        # Append system names avoiding duplicates
        for fam in sys_fonts:
            if fam in local_fonts:
                continue
            if include_paths:
                results.append((fam, None))
            else:
                results.append(fam)

        return results

