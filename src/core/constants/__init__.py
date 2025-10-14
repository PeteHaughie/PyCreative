"""Mathematical constants used across the project."""
import math

# Keep values as floats; these are thin wrappers around math.pi
PI = math.pi
HALF_PI = math.pi / 2.0
QUARTER_PI = math.pi / 4.0
TWO_PI = math.pi * 2.0
TAU = math.tau if hasattr(math, 'tau') else math.pi * 2.0
