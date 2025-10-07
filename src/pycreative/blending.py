from __future__ import annotations

from typing import Optional
from .types import RGB, RGBA

import pygame


def _apply_tint(src: pygame.Surface, tint: RGB | RGBA) -> pygame.Surface:
    """Return a copy of src with tint applied (multiply)."""
    try:
        tw, th = src.get_size()
    except Exception:
        return src

    # Try to create an SRCALPHA copy and multiply per-pixel; fall back to
    # BLEND_RGBA_MULT blit if per-pixel ops fail.
    try:
        src_copy = pygame.Surface((tw, th), flags=pygame.SRCALPHA)
        src_copy.blit(src, (0, 0))
    except Exception:
        try:
            src_copy = src.copy()
        except Exception:
            return src

    try:
        if isinstance(tint, tuple):
            if len(tint) == 3:
                r, g, b = tint
                a = 255
            else:
                r, g, b, a = tint[0], tint[1], tint[2], tint[3]
        else:
            return src

        try:
            src_copy.lock()
            for yy in range(th):
                for xx in range(tw):
                    pr, pg, pb, pa = src_copy.get_at((xx, yy))
                    nr = (pr * int(r)) // 255
                    ng = (pg * int(g)) // 255
                    nb = (pb * int(b)) // 255
                    # compute resulting alpha after tint
                    na = (pa * int(a)) // 255
                    # Premultiply RGB by resulting alpha so additive/blend ops
                    # that ignore alpha (e.g. BLEND_RGBA_ADD) behave correctly
                    # and fully-transparent pixels contribute no color.
                    try:
                        nr = (nr * na) // 255
                        ng = (ng * na) // 255
                        nb = (nb * na) // 255
                    except Exception:
                        # if any arithmetic fails, fall back to unclamped values
                        pass
                    src_copy.set_at((xx, yy), (nr, ng, nb, na))
        except Exception:
            try:
                tint_surf = pygame.Surface((tw, th), flags=pygame.SRCALPHA)
                tint_surf.fill((int(r), int(g), int(b), int(a)))
                src_copy.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            except Exception:
                return src
        finally:
            try:
                src_copy.unlock()
            except Exception:
                pass
        return src_copy
    except Exception:
        return src


def apply_blit_with_blend(dst: pygame.Surface, src: pygame.Surface, bx: int, by: int, mode: str, tint: Optional[RGB | RGBA] = None) -> None:
    """Blit `src` onto `dst` at (bx,by) applying optional tint and the named blend mode.

    Mode should be one of the Processing-style constants (strings). This
    function prefers pygame special_flags for speed and falls back to
    deterministic per-pixel implementations for SCREEN/DIFFERENCE/EXCLUSION.
    """
    src_copy = src

    # Apply tint if requested
    if tint is not None:
        try:
            src_copy = _apply_tint(src, tint)
        except Exception:
            src_copy = src

    # Normalize mode string
    try:
        m = str(mode)
    except Exception:
        m = "BLEND"

    # Map common modes to pygame blend flags where available
    try:
        if m == "ADD":
            dst.blit(src_copy, (bx, by), special_flags=pygame.BLEND_RGBA_ADD)
            return
        if m == "SUBTRACT":
            dst.blit(src_copy, (bx, by), special_flags=pygame.BLEND_RGBA_SUB)
            return
        if m == "MULTIPLY":
            dst.blit(src_copy, (bx, by), special_flags=pygame.BLEND_RGBA_MULT)
            return
        if m == "DARKEST":
            dst.blit(src_copy, (bx, by), special_flags=pygame.BLEND_RGBA_MIN)
            return
        if m == "LIGHTEST":
            dst.blit(src_copy, (bx, by), special_flags=pygame.BLEND_RGBA_MAX)
            return
        if m == "REPLACE":
            try:
                tmp = pygame.Surface(src_copy.get_size())
                tmp.blit(src_copy, (0, 0))
                dst.blit(tmp, (bx, by))
                return
            except Exception:
                dst.blit(src_copy, (bx, by))
                return

        # Per-pixel implementations for SCREEN, DIFFERENCE, EXCLUSION
        if m in ("SCREEN", "DIFFERENCE", "EXCLUSION"):
            try:
                w_s, h_s = src_copy.get_size()
            except Exception:
                return
            for yy in range(h_s):
                for xx in range(w_s):
                    dx, dy = bx + xx, by + yy
                    try:
                        sr, sg, sb, sa = src_copy.get_at((xx, yy))
                    except Exception:
                        try:
                            val = src_copy.get_at((xx, yy))
                            sr, sg, sb, sa = (val[0], val[1], val[2], val[3] if len(val) > 3 else 255)
                        except Exception:
                            continue
                    try:
                        dr, dg, db, da = dst.get_at((dx, dy))
                    except Exception:
                        continue

                    if m == "SCREEN":
                        rr = 255 - ((255 - sr) * (255 - dr) // 255)
                        gg = 255 - ((255 - sg) * (255 - dg) // 255)
                        bb = 255 - ((255 - sb) * (255 - db) // 255)
                    elif m == "DIFFERENCE":
                        rr = abs(dr - sr)
                        gg = abs(dg - sg)
                        bb = abs(db - sb)
                    else:  # EXCLUSION
                        rr = dr + sr - (2 * dr * sr // 255)
                        gg = dg + sg - (2 * dg * sg // 255)
                        bb = db + sb - (2 * db * sb // 255)

                    na = max(sa, da)
                    rr = max(0, min(255, int(rr)))
                    gg = max(0, min(255, int(gg)))
                    bb = max(0, min(255, int(bb)))
                    na = max(0, min(255, int(na)))
                    try:
                        dst.set_at((dx, dy), (rr, gg, bb, na))
                    except Exception:
                        pass
            return

        # Default: let pygame handle source-over alpha
        dst.blit(src_copy, (bx, by))
        return
    except Exception:
        try:
            dst.blit(src, (bx, by))
        except Exception:
            pass
