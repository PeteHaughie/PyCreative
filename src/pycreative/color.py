"""Color utilities (small, dependency-free helpers).

This module contains a lightweight Color class with RGB storage and HSB->RGB
conversion helpers. It is intentionally small so the rest of the library can
import it without pulling in pygame or heavier deps.
"""
from __future__ import annotations

from typing import Tuple


class Color:
    """Small color helper that stores RGB(A) and provides HSB<->RGB helpers.

    Usage:
      Color.from_rgb(255,0,0)
      Color.from_hsb(180, 100, 100, max_value=255)
    """

    def __init__(self, r: int, g: int, b: int, a: int = 255) -> None:
        self.r = int(r) & 255
        self.g = int(g) & 255
        self.b = int(b) & 255
        self.a = int(a) & 255

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def to_rgba_tuple(self) -> Tuple[int, int, int, int]:
        """Return an (r,g,b,a) tuple. Keep `to_tuple()` unchanged for back-compat.

        Use this when callers need to preserve alpha.
        """
        return (self.r, self.g, self.b, self.a)

    @staticmethod
    def _clamp_int(v: int) -> int:
        return max(0, min(255, int(v)))

    @classmethod
    def from_rgb(cls, r: float, g: float, b: float, a: float | int = 255, max_value: int = 255) -> "Color":
        try:
            # protect against invalid max_value
            mv = int(max_value)
            if mv <= 0:
                mv = 255
            # convert to normalized floats in [0,1]
            rf = float(r) / float(mv) if mv != 1 else float(r)
            gf = float(g) / float(mv) if mv != 1 else float(g)
            bf = float(b) / float(mv) if mv != 1 else float(b)
            af = float(a) / float(mv) if mv != 1 else float(a)
        except Exception:
            rf, gf, bf, af = 0.0, 0.0, 0.0, 1.0

        # clamp normalized values to [0,1]
        rf = max(0.0, min(1.0, rf))
        gf = max(0.0, min(1.0, gf))
        bf = max(0.0, min(1.0, bf))
        af = max(0.0, min(1.0, af))
        return cls(cls._clamp_int(round(rf * 255)), cls._clamp_int(round(gf * 255)), cls._clamp_int(round(bf * 255)), cls._clamp_int(round(af * 255)))

    @classmethod
    def from_hsb(
        cls,
        h: float,
        s: float,
        v: float,
        a: float | int = 255,
        max_h: int = 255,
        max_s: int | None = None,
        max_v: int | None = None,
        max_a: int | None = None,
        max_value: int | None = None,
    ) -> "Color":
        """Convert HSB/HSV to RGB.

        Arguments `max_h`, `max_s`, `max_v` specify the ranges used for the
        input components (Processing-style). If `max_s` or `max_v` are omitted
        they default to `max_h` for backward compatibility.
        """
        try:
            # Backwards-compatibility: if `max_value` is provided use it for all channels
            if max_value is not None:
                mh = int(max_value)
                ms = int(max_value)
                mv = int(max_value)
                ma = int(max_value)
            else:
                mh = int(max_h)
                ms = int(max_s) if max_s is not None else mh
                mv = int(max_v) if max_v is not None else mh
                # alpha max: fall back to mh if not provided
                ma = int(max_a) if max_a is not None else mh

            if mh <= 0:
                mh = 255
            if ms <= 0:
                ms = mh
            if mv <= 0:
                mv = mh
            if ma <= 0:
                ma = mh

            hf = float(h) / float(mh) if mh != 1 else float(h)
            sf = float(s) / float(ms) if ms != 1 else float(s)
            vf = float(v) / float(mv) if mv != 1 else float(v)
            af = float(a) / float(ma) if ma != 1 else float(a)
        except Exception:
            hf, sf, vf, af = 0.0, 0.0, 0.0, 1.0

        # normalize h into [0,1)
        hf = (hf or 0.0) % 1.0
        # clamp saturation/value into [0,1]
        sf = max(0.0, min(1.0, sf or 0.0))
        vf = max(0.0, min(1.0, vf or 0.0))
        # clamp alpha into [0,1]
        af = max(0.0, min(1.0, af or 0.0))

        if sf <= 0.0:
            val = cls._clamp_int(round(vf * 255))
            alpha_val = cls._clamp_int(round(af * 255))
            return cls(val, val, val, alpha_val)

        i = int(hf * 6.0)  # sector 0..5
        f = (hf * 6.0) - i
        p = vf * (1.0 - sf)
        q = vf * (1.0 - sf * f)
        t = vf * (1.0 - sf * (1.0 - f))
        i = i % 6
        if i == 0:
            r, g, b = vf, t, p
        elif i == 1:
            r, g, b = q, vf, p
        elif i == 2:
            r, g, b = p, vf, t
        elif i == 3:
            r, g, b = p, q, vf
        elif i == 4:
            r, g, b = t, p, vf
        else:
            r, g, b = vf, p, q

        return cls(cls._clamp_int(round(r * 255)), cls._clamp_int(round(g * 255)), cls._clamp_int(round(b * 255)), cls._clamp_int(round(af * 255)))

    def __repr__(self) -> str:
        return f"Color(r={self.r},g={self.g},b={self.b},a={self.a})"

    def to_hsb(self, max_h: int = 255, max_s: int | None = None, max_v: int | None = None, max_a: int | None = None, max_value: int | None = None) -> tuple[int, int, int, int]:
        """Convert stored RGB(A) to HSB/HSV scaled to the provided maxima.

        Returns (h, s, v, a) as integers scaled to (max_h, max_s, max_v, max_a).
        Uses similar defaulting rules as from_hsb/from_rgb: if max_value is
        provided, it is used for all channels; otherwise unspecified maxes
        defer to max_h.
        """
        try:
            if max_value is not None:
                mh = int(max_value)
                ms = int(max_value)
                mv = int(max_value)
                ma = int(max_value)
            else:
                mh = int(max_h)
                ms = int(max_s) if max_s is not None else mh
                mv = int(max_v) if max_v is not None else mh
                ma = int(max_a) if max_a is not None else mh
        except Exception:
            mh, ms, mv, ma = 255, 255, 255, 255

        mh = mh if mh > 0 else 255
        ms = ms if ms > 0 else mh
        mv = mv if mv > 0 else mh
        ma = ma if ma > 0 else mh

        # normalize RGB to [0,1]
        rf = self.r / 255.0
        gf = self.g / 255.0
        bf = self.b / 255.0

        maxc = max(rf, gf, bf)
        minc = min(rf, gf, bf)
        delta = maxc - minc

        # Hue calculation
        if delta == 0:
            h = 0.0
        else:
            if maxc == rf:
                h = ((gf - bf) / delta) % 6.0
            elif maxc == gf:
                h = ((bf - rf) / delta) + 2.0
            else:
                h = ((rf - gf) / delta) + 4.0
            h = h / 6.0  # scale to [0,1)

        # Saturation
        s = 0.0 if maxc == 0 else (delta / maxc)
        # Brightness/value
        v = maxc

        # scale to requested integer ranges
        H = self._clamp_int(round(h * mh))
        S = self._clamp_int(round(s * ms))
        V = self._clamp_int(round(v * mv))
        A = self._clamp_int(round((self.a / 255.0) * ma))

        return (H, S, V, A)
