"""Color utilities used across core packages.

Keep pure, side-effect-free conversion helpers here so tests can import
them without pulling in engine internals.
"""
# Re-export small, pure conversion helpers from dedicated modules
from core.color.hsb_to_rgb import hsb_to_rgb as hsb_to_rgb
from core.color.rgb_to_hsb import rgb_to_hsb as rgb_to_hsb

__all__ = [
    'hsb_to_rgb',
    'rgb_to_hsb',
    'color', 'red', 'green', 'blue', 'alpha', 'lerp_color',
]


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def color(*args):
    """Create a 32-bit ARGB color integer.

    Supports variants:
    - color(gray)
    - color(gray, alpha)
    - color(r, g, b)
    - color(r, g, b, a)

    Components may be given as 0..1 floats or 0..255 ints; outputs are ints.
    """
    a = 255
    if len(args) == 0:
        raise TypeError('color() requires at least one argument')
    if len(args) == 1:
        v = args[0]
        vf = float(v)
        if vf <= 1:
            gray = int(round(vf * 255))
        else:
            gray = int(round(vf))
        r = g = b = gray
    elif len(args) == 2:
        v, a_in = args
        vf = float(v)
        if vf <= 1:
            gray = int(round(vf * 255))
        else:
            gray = int(round(vf))
        r = g = b = gray
        af = float(a_in)
        a = int(round(af * 255)) if af <= 1 else int(round(af))
    elif len(args) == 3 or len(args) == 4:
        r_in, g_in, b_in = args[0], args[1], args[2]
        af = args[3] if len(args) == 4 else 255
        def conv(x):
            xf = float(x)
            return int(round(xf * 255)) if xf <= 1 else int(round(xf))
        r = conv(r_in)
        g = conv(g_in)
        b = conv(b_in)
        a = conv(af)
    else:
        raise TypeError('color() accepts 1 to 4 arguments')

    # clamp components to byte range
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    a = max(0, min(255, int(a)))

    return (a << 24) | (r << 16) | (g << 8) | b


def red(c: int) -> float:
    return float((int(c) >> 16) & 0xFF)


def green(c: int) -> float:
    return float((int(c) >> 8) & 0xFF)


def blue(c: int) -> float:
    return float(int(c) & 0xFF)


def alpha(c: int) -> float:
    return float((int(c) >> 24) & 0xFF)


def lerp_color(c1: int, c2: int, amt: float) -> int:
    """Interpolate between two ARGB colors; amt is clamped to [0,1]."""
    t = _clamp01(amt)
    a1 = (int(c1) >> 24) & 0xFF
    r1 = (int(c1) >> 16) & 0xFF
    g1 = (int(c1) >> 8) & 0xFF
    b1 = int(c1) & 0xFF

    a2 = (int(c2) >> 24) & 0xFF
    r2 = (int(c2) >> 16) & 0xFF
    g2 = (int(c2) >> 8) & 0xFF
    b2 = int(c2) & 0xFF

    def mix(u, v):
        return int(round((1 - t) * u + t * v))

    a = mix(a1, a2)
    r = mix(r1, r2)
    g = mix(g1, g2)
    b = mix(b1, b2)

    return (a << 24) | (r << 16) | (g << 8) | b
