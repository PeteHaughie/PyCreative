import math

from pycreative import constants


def test_constants_values():
    assert math.isclose(constants.PI, math.pi)
    assert math.isclose(constants.HALF_PI, math.pi / 2.0)
    assert math.isclose(constants.QUARTER_PI, math.pi / 4.0)
    assert math.isclose(constants.TWO_PI, math.pi * 2.0)
    # TAU may or may not exist in math; ensure it's equivalent to 2*pi
    assert math.isclose(constants.TAU, math.tau if hasattr(math, 'tau') else math.pi * 2.0)
