"""Convenience method bindings for class-based sketches.

Centralized list of method names that should be attached to Sketch
instances so authors can write `self.size()`, `self.constrain()`, etc.
Keep this list small and documented; tests can import this constant to
assert class-based sketches expose the expected API.
"""

SKETCH_CONVENIENCE_METHODS = (
    'size', 'background', 'window_title', 'no_loop', 'loop', 'redraw', 'save_frame',
    'rect', 'line', 'circle', 'square', 'frame_rate',
    'fill', 'stroke', 'stroke_weight',
    # Math helpers and random API commonly used in examples
    'constrain', 'lerp', 'map', 'dist',
    'point', 'random', 'random_seed', "random_gaussian",
    'no_fill', 'no_stroke',
)

__all__ = ['SKETCH_CONVENIENCE_METHODS']
