from __future__ import annotations

from typing import List, Tuple, Optional
from ..graphics import Surface


class PShape:
    """Simple vector shape container.

    Stores subpaths as lists of (x, y) coordinates. Style attributes are
    intentionally minimal and mirror the previous monolithic implementation.
    """

    def __init__(self) -> None:
        self.subpaths: List[List[Tuple[float, float]]] = []
        # backing fields for style properties
        self._fill = None
        # SVG default: no stroke unless specified
        self._stroke = None
        self._stroke_weight = 1
        self.stroke_linecap = None
        self.stroke_linejoin = None
        self.stroke_miterlimit = None
        self.stroke_dasharray = None
        self.fill_rule = None
        self._style_enabled: bool = True
        self.view_box: Optional[Tuple[float, float, float, float]] = None
        # Supersample factor for higher-fidelity rendering (1 = off)
        self.supersample: int = 1
        # version counter for cache invalidation when shape mutates
        self._version: int = 1

    def add_subpath(self, pts: List[Tuple[float, float]]) -> None:
        if pts:
            self.subpaths.append(pts)
            self._version += 1

    # Style properties with auto-invalidate so cached rasters are refreshed
    @property
    def fill(self):
        return getattr(self, '_fill', None)

    @fill.setter
    def fill(self, v):
        self._fill = v
        self.invalidate()

    @property
    def stroke(self):
        return getattr(self, '_stroke', None)

    @stroke.setter
    def stroke(self, v):
        self._stroke = v
        self.invalidate()

    @property
    def stroke_weight(self):
        return getattr(self, '_stroke_weight', None)

    @stroke_weight.setter
    def stroke_weight(self, v):
        try:
            self._stroke_weight = int(v) if v is not None else v
        except Exception:
            self._stroke_weight = v
        self.invalidate()

    def invalidate(self) -> None:
        """Bump internal version to indicate the shape changed (cache invalidation)."""
        try:
            self._version += 1
        except Exception:
            self._version = getattr(self, '_version', 1) + 1

    def enable_style(self) -> None:
        self._style_enabled = True

    def disable_style(self) -> None:
        self._style_enabled = False

    def draw(self, surface: Surface, x: float = 0, y: float = 0, w: Optional[float] = None, h: Optional[float] = None) -> None:
        # Support optional supersampling: if supersample>1, render to an
        # offscreen high-res surface and downsample into the provided surface.
        ss = int(getattr(self, 'supersample', 1))
        if ss > 1 and w is not None and h is not None:
            # create a temporary high-res pygame surface and wrapper Surface
            try:
                import pygame
                from ..graphics import Surface as GraphicsSurface
                hi_w = int(w) * ss
                hi_h = int(h) * ss
                raw = pygame.Surface((hi_w, hi_h), flags=pygame.SRCALPHA)
                hi_surf = GraphicsSurface(raw)
                # draw into hi_surf with scaled target size
                self._draw_on_surface(hi_surf, 0, 0, hi_w, hi_h)
                # downsample hi_surf into destination
                # use pygame.image.tostring -> PIL for high-quality resample
                try:
                    from PIL import Image
                    im = Image.frombuffer('RGBA', raw.get_size(), pygame.image.tostring(raw, 'RGBA'), 'raw', 'RGBA', 0, 1)
                    im = im.resize((int(w), int(h)), Image.Resampling.LANCZOS)
                    # blit back to destination surface
                    import io
                    out_surf = surface.raw
                    mode = 'RGBA'
                    pg_img = pygame.image.fromstring(im.tobytes(), im.size, mode)
                    out_surf.blit(pg_img, (int(x), int(y)))
                    return
                except Exception:
                    # fallback: nearest-downsample via pygame
                    scaled = pygame.transform.smoothscale(raw, (int(w), int(h)))
                    surface.raw.blit(scaled, (int(x), int(y)))
                    return
            except Exception:
                # if anything goes wrong, fall back to regular draw
                pass

        # Normal path: draw directly into provided surface
        # Preferred path: when Skia is available, rasterize the PShape with
        # Skia at the requested target size (cached) and blit the produced
        # PIL image into the pygame surface. This gives highest visual
        # fidelity by default. Fall back to any attached raster or the
        # vector draw path on failure.
        try:
            from . import skia_loader
            if getattr(skia_loader, 'skia_available', lambda: False)() and w is not None and h is not None:
                try:
                    from .skia_renderer import skia_rasterize_pshape_cached
                    pil_img = skia_rasterize_pshape_cached(self, int(w), int(h))
                    if pil_img is not None:
                        import pygame
                        from PIL import Image
                        if not hasattr(pil_img, 'mode'):
                            raise TypeError('skia raster not a PIL image')
                        im = pil_img.convert('RGBA') if pil_img.mode != 'RGBA' else pil_img
                        resized = im.resize((int(w), int(h)), Image.Resampling.BOX) if im.size != (int(w), int(h)) else im
                        pg_img = pygame.image.fromstring(resized.tobytes(), resized.size, 'RGBA')
                        surface.raw.blit(pg_img, (int(x), int(y)))
                        return
                except Exception:
                    # on any skia rasterization error, fall through to existing behavior
                    pass

        except Exception:
            # defensive: ignore skia import or runtime errors and continue
            pass

        # Back-compat fallback: if a loader attached a precomputed raster, try blitting it
        try:
            pil_img = getattr(self, '_skia_raster', None)
            if pil_img is not None and w is not None and h is not None:
                try:
                    import pygame
                    from PIL import Image
                    if not hasattr(pil_img, 'mode'):
                        raise TypeError('attached skia raster not a PIL image')
                    im = pil_img.convert('RGBA') if pil_img.mode != 'RGBA' else pil_img
                    resized = im.resize((int(w), int(h)), Image.Resampling.BOX)
                    pg_img = pygame.image.fromstring(resized.tobytes(), resized.size, 'RGBA')
                    surface.raw.blit(pg_img, (int(x), int(y)))
                    return
                except Exception:
                    pass
        except Exception:
            pass

        self._draw_on_surface(surface, x, y, w, h)
        return

    def _draw_on_surface(self, surface: Surface, x: float = 0, y: float = 0, w: Optional[float] = None, h: Optional[float] = None) -> None:
        # Core drawing logic extracted to allow supersampling fallback.
        # Compute source bounds
        if self.view_box is not None:
            # Use the declared SVG viewBox exactly. We'll map the viewBox
            # into the provided target rectangle using preserveAspectRatio
            # behavior 'xMidYMid meet' (scale = min(scale_x, scale_y),
            # centered). This ensures a like-for-like transform with Skia's
            # SVGDOM rendering used in tests.
            vb_x, vb_y, vb_w, vb_h = self.view_box
            # defend against degenerate viewBox sizes
            if vb_w == 0:
                vb_w = 1.0
            if vb_h == 0:
                vb_h = 1.0
            # We'll compute scale/offset per SVG preserveAspectRatio semantics
            # only when both target w and h are provided; otherwise fall back
            # to previous behavior which fits bounds independently.
            if w is not None and h is not None:
                try:
                    sx = float(w) / float(vb_w)
                except Exception:
                    sx = 1.0
                try:
                    sy = float(h) / float(vb_h)
                except Exception:
                    sy = 1.0
                scale = min(sx, sy)
                # center the scaled viewBox inside the target rect
                extra_x = float(w) - (vb_w * scale)
                extra_y = float(h) - (vb_h * scale)
                offset_x = x + (extra_x / 2.0) - (vb_x * scale)
                offset_y = y + (extra_y / 2.0) - (vb_y * scale)
                # store mapping params so inner loop uses the SVG mapping
                map_scale_x = scale
                map_scale_y = scale
                map_offset_x = offset_x
                map_offset_y = offset_y
            else:
                # fallback: map viewBox directly to origin without centering
                map_scale_x = (float(w) / vb_w) if w is not None else 1.0
                map_scale_y = (float(h) / vb_h) if h is not None else 1.0
                map_offset_x = -vb_x * map_scale_x + (x if x is not None else 0.0)
                map_offset_y = -vb_y * map_scale_y + (y if y is not None else 0.0)
            # set min_x/min_y/orig_w/orig_h util values for downstream code
            min_x = vb_x
            min_y = vb_y
            orig_w = vb_w
            orig_h = vb_h
        else:
            min_x = float('inf')
            min_y = float('inf')
            max_x = float('-inf')
            max_y = float('-inf')
            for sub in self.subpaths:
                for px, py in sub:
                    if px < min_x:
                        min_x = px
                    if py < min_y:
                        min_y = py
                    if px > max_x:
                        max_x = px
                    if py > max_y:
                        max_y = py

        if min_x == float('inf'):
            return

        # If a viewBox mapping was computed above we already have orig_w/orig_h
        try:
            _ = map_scale_x  # type: ignore
            # map_scale_x/_y/_offset_x/_y are defined when viewBox mapping used
            orig_w = orig_w if 'orig_w' in locals() else (max_x - min_x if max_x > min_x else 1.0)
            orig_h = orig_h if 'orig_h' in locals() else (max_y - min_y if max_y > min_y else 1.0)
        except Exception:
            orig_w = max_x - min_x if max_x > min_x else 1.0
            orig_h = max_y - min_y if max_y > min_y else 1.0

        scale_x = 1.0
        scale_y = 1.0
        if w is not None:
            try:
                scale_x = float(w) / orig_w
            except Exception:
                scale_x = 1.0
        if h is not None:
            try:
                scale_y = float(h) / orig_h
            except Exception:
                scale_y = 1.0

        if w is not None and h is None:
            scale_y = scale_x
        if h is not None and w is None:
            scale_x = scale_y

        for sub in self.subpaths:
            pts: List[Tuple[float, float]] = []
            for px, py in sub:
                # If we computed an explicit viewBox->target mapping use it
                # (scale + offset); otherwise fall back to uniform scaling
                # computed from orig_w/orig_h above.
                if 'map_scale_x' in locals():
                    sx = px * map_scale_x + map_offset_x
                    sy = py * map_scale_y + map_offset_y
                else:
                    sx = (px - min_x) * scale_x
                    sy = (py - min_y) * scale_y
                    sx = x + sx
                    sy = y + sy
                pts.append((sx, sy))
            fill = self.fill if self._style_enabled else None
            stroke = self.stroke if self._style_enabled else None
            stroke_weight = self.stroke_weight if self._style_enabled else None

            # Decide whether the subpath should be treated as closed. Historically
            # we relied on an explicit close (Z/z) verb to append the start
            # point; however some loader code paths can produce contours where
            # the closing point wasn't preserved. For robust rendering we
            # consider any subpath with three or more points to be a filled
            # polygon (matching common SVG usage). This is pragmatic and can
            # be refined later to track explicit-closure flags per-subpath.
            if len(pts) >= 3:
                surface.polygon_with_style(pts, fill=fill, stroke=stroke, stroke_weight=stroke_weight)
            else:
                surface.polyline_with_style(pts, stroke=stroke, stroke_weight=stroke_weight)
