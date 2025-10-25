"""Convenience method bindings for class-based sketches.

Centralized list of method names that should be attached to Sketch
instances so authors can write `self.size()`, `self.constrain()`, etc.
Keep this list small and documented; tests can import this constant to
assert class-based sketches expose the expected API.
"""

SKETCH_CONVENIENCE_METHODS = (
    'size', 'background', 'window_title', 'no_loop', 'loop', 'redraw', 'save_frame',
    'rect', 'line', 'circle', 'square', 'frame_rate',
    'ellipse',
    'fill', 'stroke', 'stroke_weight',
    # shape attribute helpers
    'ellipse_mode',
    # Math helpers and random API commonly used in examples
    # expose the common math calculation helpers so sketches can call
    # `self.map()`, `self.lerp()`, `self.norm()`, etc.
    'abs', 'ceil', 'floor', 'constrain', 'dist', 'lerp', 'mag', 'map',
    'sq', 'sqrt', 'pow', 'max', 'min', 'round', 'exp', 'log', 'norm',
    # trig & angle helpers
    'sin', 'cos', 'tan', 'radians', 'degrees',
    'point', 'random', 'random_seed', "random_gaussian",
    'uniform',
    'pcvector',
    'noise', 'noise_seed', 'noise_detail',
    'no_fill', 'no_stroke',
    # Shape recording helpers
    'begin_shape', 'vertex', 'end_shape',
    # Transform helpers (2D)
    'translate', 'rotate', 'scale', 'push_matrix', 'pop_matrix', 'pushMatrix', 'popMatrix',
    'shear_x', 'shear_y', 'reset_matrix', 'apply_matrix',
    'image', 'image_mode',
)

__all__ = ['SKETCH_CONVENIENCE_METHODS']
