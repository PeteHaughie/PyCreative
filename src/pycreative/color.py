"""
pycreative.color: Color utility class for creative coding.
"""

from typing import Tuple


class Color:
    """
    RGB color utility class.
    """

    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b})"

    def as_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)

    @classmethod
    def from_hex(cls, hex_str: str):
        hex_str = hex_str.lstrip("#")
        if len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return cls(r, g, b)
        raise ValueError("Hex string must be 6 characters")

    def lighten(self, amount: float):
        return Color(
            min(int(self.r + 255 * amount), 255),
            min(int(self.g + 255 * amount), 255),
            min(int(self.b + 255 * amount), 255),
        )

    def darken(self, amount: float):
        return Color(
            max(int(self.r - 255 * amount), 0),
            max(int(self.g - 255 * amount), 0),
            max(int(self.b - 255 * amount), 0),
        )
