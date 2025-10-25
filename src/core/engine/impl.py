"""Minimal headless Engine implementation for tests and development.

This implementation focuses on headless execution: it records drawing
commands to an in-memory buffer (`graphics.commands`) so tests can assert
behaviour without opening windows or touching GPU libraries.

Not a production implementation — replace with real Engine when ready.
"""
from __future__ import annotations

import os
from contextlib import redirect_stderr
from typing import Any, Callable, Optional

from core.adapters.skia_gl_present import SkiaGLPresenter
from core.graphics import GraphicsBuffer

from .api import SimpleSketchAPI
from .api.registry import APIRegistry


class Engine:
    """A tiny headless engine for testing sketches.

    Lifecycle behaviour implemented:
    - call `setup(this)` once before the first draw
    - call `draw(this)` each frame depending on loop/no_loop/redraw
    - expose minimal helpers: size, no_loop, loop, redraw, save_frame
    """

    def __init__(
        self,
        sketch_module: Optional[Any] = None,
        headless: bool = True,
        present_mode: Optional[str] = None,
        force_gles: bool = False,
    ):
        self._no_loop_drawn = False
        # store original sketch module passed to the Engine (if any).
        # This keeps a stable reference to the file the CLI loaded so
        # snapshot/save_frame can resolve relative paths to the sketch
        # folder even after `self.sketch` is normalized/instantiated.
        self._sketch_module = sketch_module
        self.sketch = sketch_module
        self.headless = headless
        self.api = APIRegistry()
        self.graphics = GraphicsBuffer()

        # lifecycle & environment
        self._setup_done = False
        self.looping = True
        self._redraw_requested = False
        # default frame rate (60 fps). A value of -1 means unrestricted.
        self.frame_rate = 60
        self.frame_count = 0
        # default size (can be overridden by sketch.size())
        # per API contract: default window is 200x200 when size() not called
        self.width = 200
        self.height = 200
        # default background color: rgb(200)
        self.background_color = (200, 200, 200)
        # drawing state
        # None means no fill/stroke; colors are (r,g,b) tuples
        self.fill_color: Optional[tuple] = (255, 255, 255)
        self.stroke_color: Optional[tuple] = (0, 0, 0)
        self.stroke_weight: int = 1
        # Mouse/input state (defaults per docs)
        # mouse_x/y report current mouse coords (int); pmouse_x/y are previous
        self.mouse_x: int = 0
        self.mouse_y: int = 0
        self.pmouse_x: int = 0
        self.pmouse_y: int = 0
        # mouse_pressed boolean and mouse_button ('LEFT'|'RIGHT'|'CENTER'|None)
        self.mouse_pressed: bool = False
        self.mouse_button: Optional[str] = None
        # color mode: 'RGB' or 'HSB' (case-insensitive). Default RGB.
        self.color_mode = 'RGB'
        # pluggable snapshot backend: callable(path, width, height, engine)
        # default is None (the engine will attempt a Pillow-based write)
        # Keep un-annotated to avoid long type expressions in this file.
        self.snapshot_backend = None

        # Normalize sketch: if a module contains a `Sketch` class, instantiate it
        # Register default API functions so SimpleSketchAPI delegates work
        # and class-based sketch instances can be bound to these helpers.
        try:
            from core.engine.api.registrations import (
                register_math,
                register_random_and_noise,
                register_shape_apis,
            )
            try:
                register_shape_apis(self)
            except Exception:
                pass
            try:
                register_random_and_noise(self)
            except Exception:
                pass
            try:
                register_math(self)
            except Exception:
                pass
        except Exception:
            # best-effort only; continue if registrations can't be imported
            pass

        # Normalize sketch: if a module contains a `Sketch` class, instantiate it
        self._normalize_sketch()

        # If the user provided a direct sketch instance (not a module with a
        # `Sketch` class), attempt to attach convenience API functions as
        # bound methods on the instance. This mirrors the behaviour when the
        # engine instantiates a Sketch class and keeps tests/examples that
        # construct an instance directly working.
        try:
            s = getattr(self, 'sketch', None)
            if s is not None:
                try:
                    from core.engine.bindings import SKETCH_CONVENIENCE_METHODS
                    _sketch_methods = list(SKETCH_CONVENIENCE_METHODS)
                except Exception:
                    _sketch_methods = []

                for name in _sketch_methods:
                    # don't overwrite user-defined members
                    if hasattr(s, name):
                        continue
                    try:
                        fn = self.api.get(name)
                        if callable(fn):
                            try:
                                setattr(s, name, fn)
                            except Exception:
                                # best-effort only
                                pass
                    except Exception:
                        pass
        except Exception:
            pass

        # Debugging toggle: when True, exceptions raised by user handlers
        # will be re-raised instead of swallowed. Can be enabled via
        # environment variable PYCREATIVE_DEBUG_HANDLER_EXCEPTIONS.
        try:
            self._debug_handler_exceptions = bool(
                int(os.getenv('PYCREATIVE_DEBUG_HANDLER_EXCEPTIONS', '0'))
            )
        except Exception:
            self._debug_handler_exceptions = False

        self._running = False
        # store desired presenter mode if provided (None | 'vbo' | 'blit' | 'immediate')
        self.present_mode = present_mode
        # optional force GLES flag (for testing on platforms with GLES support)
        self.force_gles = bool(force_gles)

        # Register default API functions so SimpleSketchAPI delegates work
        try:
            from core.engine.registrations import (
                register_random_and_noise,
                register_shape_apis,
            )
            try:
                register_shape_apis(self)
            except Exception:
                pass
            try:
                register_random_and_noise(self)
            except Exception:
                pass
        except Exception:
            # best-effort only; continue if registrations can't be imported
            pass

        # Register simple color/stroke ops via central registrations helper.
        try:
            from core.engine.registrations import register_state_apis
            try:
                register_state_apis(self)
            except Exception:
                pass
        except Exception:
            #best-effort only
            pass

        # Register image APIs via api registrations
        try:
            from core.engine.api.registrations import register_image_apis
            try:
                register_image_apis(self)
            except Exception:
                pass
        except Exception:
            pass
        except Exception:
            # best-effort only; continue if registrations can't be imported
            pass


    def register_api(self, registrant: Callable[["Engine"], None]):
        """Call a module's register_api(engine) hook to wire API functions.

        Accepts either a callable that will be invoked with the Engine, or
        a module-like object with a `register_api` attribute.
        """
        # Prefer module-like objects that expose `register_api` to avoid
        # treating classes (which are callable) as functions.
        if hasattr(registrant, 'register_api'):
            registrant.register_api(self)
            return
        if callable(registrant):
            # registrant is a function that accepts engine
            registrant(self)
            return
        raise TypeError('registrant must be callable or have register_api')

    def _normalize_sketch(self):
        """If the provided sketch is a module that defines a Sketch class,
        instantiate it so we always operate on an object with methods.
        """
        s = self.sketch
        if s is None:
            return
        # module with Sketch class
        if hasattr(s, 'Sketch') and isinstance(getattr(s, 'Sketch'), type):
            try:
                inst = s.Sketch()
                # Expose the engine on the instance so dynamic properties
                # (e.g., width/height) can access it without depending on
                # how API callables were attached.
                try:
                    setattr(inst, '_engine', self)
                except Exception:
                    pass
                # Attach a SimpleSketchAPI facade onto the instance so class-based
                # sketches can call self.size(), self.background(), etc.
                api = SimpleSketchAPI(self)
                # If this is a class-based sketch instance, create a tiny
                # dynamic subclass that exposes `width` and `height` as
                # properties delegating to the engine. This allows sketch
                # authors to use `self.width` inside class-based sketches.
                try:
                    cls = inst.__class__
                    if not hasattr(cls, 'width') and not hasattr(cls, 'height'):
                        def _make_width_prop():
                            def _getter(self_obj):
                                return int(getattr(self_obj._engine, 'width', 0))

                            return property(_getter)

                        def _make_height_prop():
                            def _getter(self_obj):
                                return int(getattr(self_obj._engine, 'height', 0))

                            return property(_getter)

                        def _make_mouse_x_prop():
                            def _getter(self_obj):
                                return int(getattr(self_obj._engine, 'mouse_x', 0))

                            return property(_getter)

                        def _make_mouse_y_prop():
                            def _getter(self_obj):
                                return int(getattr(self_obj._engine, 'mouse_y', 0))

                            return property(_getter)

                        def _make_pmouse_x_prop():
                            def _getter(self_obj):
                                return int(getattr(self_obj._engine, 'pmouse_x', 0))

                            return property(_getter)

                        def _make_pmouse_y_prop():
                            def _getter(self_obj):
                                return int(getattr(self_obj._engine, 'pmouse_y', 0))

                            return property(_getter)

                        def _make_mouse_button_prop():
                            def _getter(self_obj):
                                return getattr(self_obj._engine, 'mouse_button', None)

                            return property(_getter)

                        def _make_key_prop():
                            def _getter(self_obj):
                                return getattr(self_obj._engine, 'key', None)

                            return property(_getter)

                        def _make_key_code_prop():
                            def _getter(self_obj):
                                return getattr(self_obj._engine, 'key_code', None)

                            return property(_getter)

                        def _make_frame_count_prop():
                            def _getter(self_obj):
                                try:
                                    return int(getattr(self_obj._engine, 'frame_count', 0))
                                except Exception:
                                    return 0

                            return property(_getter)

                        # Create a descriptor that exposes a read-only boolean
                        # view of engine.mouse_pressed while still allowing
                        # the user-defined `mouse_pressed()` handler to be
                        # invoked if the developer calls it as a function.
                        class _MousePressedProxy:
                            def __init__(self, handler=None):
                                # handler is the original unbound function from the
                                # user's class (may be None)
                                self._handler = handler

                            def __get__(self, instance, owner=None):
                                # Return a bound proxy object that is both bool-like
                                # and callable (if a handler exists).
                                if instance is None:
                                    return self

                                class _Bound:
                                    def __init__(self, inst, handler):
                                        self._inst = inst
                                        self._handler = handler

                                    def __bool__(self):
                                        try:
                                            inst_ref = self._inst
                                            eng_attr = '_engine'
                                            e = getattr(inst_ref, eng_attr, None)
                                            val = getattr(e, 'mouse_pressed', False)
                                            return bool(val)
                                        except Exception:
                                            return False
                                    # allow int(self.mouse_pressed) or contexts that
                                    # check truthiness
                                    def __int__(self):
                                        return 1 if bool(self) else 0

                                    def __call__(self, *a, **kw):
                                        # If user defined a handler, call it with the
                                        # instance as first arg (bound semantics).
                                        if callable(self._handler):
                                            try:
                                                handler_fn = self._handler
                                                args_tuple = (self._inst,) + a
                                                return handler_fn(*args_tuple, **kw)
                                            except Exception:
                                                e = getattr(self._inst, '_engine', None)
                                                dbg = False
                                                if e is not None:
                                                    dbg = getattr(
                                                        e,
                                                        '_debug_handler_exceptions',
                                                        False,
                                                    )
                                                if dbg:
                                                    raise
                                                return None
                                        # no handler defined: noop
                                        return None

                                    def __repr__(self):
                                        try:
                                            b = bool(self)
                                            return "<mouse_pressed proxy %s>" % b
                                        except Exception:
                                            return "<mouse_pressed proxy>"

                                return _Bound(instance, self._handler)

                        # Capture the original unbound mouse_pressed function if present
                        orig_mouse_pressed = None
                        try:
                            m = getattr(cls, 'mouse_pressed', None)
                            if callable(m):
                                # store the unbound function so the proxy can call it
                                orig_mouse_pressed = m
                        except Exception:
                            orig_mouse_pressed = None

                        # Capture the original unbound key_pressed function if present
                        orig_key_pressed = None
                        try:
                            k = getattr(cls, 'key_pressed', None)
                            if callable(k):
                                orig_key_pressed = k
                        except Exception:
                            orig_key_pressed = None

                        # Provide a __getattr__ on the dynamic subclass to forward
                        # missing convenience methods to the SimpleSketchAPI facade
                        # (available as `api` in this scope). This avoids needing to
                        # attach every possible helper individually and keeps the
                        # sketch instance API ergonomic.
                        def _make_getattr(api_ref):
                            def __getattr__(self, name):
                                # Provide small, local fallbacks for common
                                # convenience methods used by examples if they
                                # were not attached earlier.
                                if name == 'rect_mode':
                                    def _rm(m):
                                        try:
                                            self._engine.rect_mode = str(m)
                                        except Exception:
                                            pass
                                    return _rm
                                if name == 'ellipse_mode':
                                    def _em(m):
                                        try:
                                            self._engine.ellipse_mode = str(m)
                                        except Exception:
                                            pass
                                    return _em
                                if name == 'image_mode':
                                    def _im(m):
                                        try:
                                            # normalize common names
                                            self._engine.image_mode = str(m)
                                        except Exception:
                                            pass
                                    return _im
                                if name == 'no_cursor':
                                    def _nc():
                                        try:
                                            self._engine._no_cursor = True
                                        except Exception:
                                            pass
                                    return _nc
                                if name == 'no_stroke':
                                    def _ns():
                                        try:
                                            self._engine.stroke_color = None
                                        except Exception:
                                            pass
                                    return _ns
                                if name == 'no_fill':
                                    def _nf():
                                        try:
                                            self._engine.fill_color = None
                                        except Exception:
                                            pass
                                    return _nf
                                # Forward to the API facade if available
                                try:
                                    if hasattr(api_ref, name):
                                            attr = getattr(api_ref, name)
                                            # If the API facade exposes a callable (bound
                                            # method or callable object), return it directly
                                            # rather than wrapping it in a plain function.
                                            # Wrapping loses attributes (e.g. factory
                                            # helpers like pcvector.random2d) and also
                                            # turns bound methods into plain functions
                                            # which breaks the Engine's call semantics
                                            # that rely on detecting __self__ for bound
                                            # methods.
                                            return attr
                                except Exception:
                                    pass
                                raise AttributeError(name)
                            return __getattr__

                        # create a short-lived proxy instance to avoid an overly long
                        # literal expression when inserting into the attrs dict
                        _mouse_pressed_proxy = _MousePressedProxy(
                            handler=orig_mouse_pressed,
                        )

                        attrs = {
                            'width': _make_width_prop(),
                            'height': _make_height_prop(),
                            'frame_count': _make_frame_count_prop(),
                            'mouse_x': _make_mouse_x_prop(),
                            'mouse_y': _make_mouse_y_prop(),
                            'pmouse_x': _make_pmouse_x_prop(),
                            'pmouse_y': _make_pmouse_y_prop(),
                            'mouse_button': _make_mouse_button_prop(),
                            'mouse_pressed': _mouse_pressed_proxy,
                            # read-only properties backed by the engine
                            'key': _make_key_prop(),
                            'key_code': _make_key_code_prop(),
                            # key_pressed: proxy object (bool-like, callable)
                            'key_pressed': None,
                            '__getattr__': _make_getattr(api),
                        }
                        Dynamic = type(f"{cls.__name__}_WithEnv", (cls,), attrs)
                        # Attach a KeyPressed proxy descriptor after Dynamic creation so
                        # we can reuse the same pattern as mouse_pressed while allowing
                        # the descriptor to capture the original unbound handler.
                        try:
                            class _KeyPressedProxy:
                                def __init__(self, handler=None):
                                    self._handler = handler

                                def __get__(self, instance, owner=None):
                                    if instance is None:
                                        return self

                                    class _Bound:
                                        def __init__(self, inst, handler):
                                            self._inst = inst
                                            self._handler = handler

                                        def __bool__(self):
                                            try:
                                                inst_ref = self._inst
                                                e = getattr(inst_ref, '_engine', None)
                                                val = getattr(e, 'key_pressed', False)
                                                return bool(val)
                                            except Exception:
                                                return False

                                        def __int__(self):
                                            return 1 if bool(self) else 0

                                        def __call__(self, *a, **kw):
                                            if callable(self._handler):
                                                try:
                                                    handler_fn = self._handler
                                                    args_tuple = (self._inst,) + a
                                                    return handler_fn(*args_tuple, **kw)
                                                except Exception:
                                                    inst_ref = self._inst
                                                    # short local for getattr
                                                    _ga = getattr
                                                    e = _ga(inst_ref, '_engine', None)
                                                    dbg = False
                                                    if e is not None:
                                                        dbg = getattr(
                                                            e,
                                                            '_debug_handler_exceptions',
                                                            False,
                                                        )
                                                    if dbg:
                                                        raise
                                                    return None
                                            return None

                                        def __repr__(self):
                                            try:
                                                b = bool(self)
                                                return "<key_pressed proxy %s>" % b
                                            except Exception:
                                                return "<key_pressed proxy>"

                                    return _Bound(instance, self._handler)

                            # set the descriptor on the Dynamic class
                            _kp = _KeyPressedProxy(handler=orig_key_pressed)
                            setattr(Dynamic, 'key_pressed', _kp)
                        except Exception:
                            # ignore failures to attach descriptor
                            pass
                        try:
                            inst.__class__ = Dynamic
                        except Exception:
                            # If assignment fails for some types, silently continue
                            pass
                except Exception:
                    pass
                # Load the canonical binding list from the engine bindings
                # module. Fall back to an inline list if the import fails so
                # early boot or tests without the module still work.
                from typing import Sequence
                # Declare _sketch_methods once and assign in branches to avoid
                # static redefinition errors from type checkers.
                _sketch_methods: Sequence[str]
                try:
                    from core.engine.bindings import SKETCH_CONVENIENCE_METHODS
                    # Normalize to a sequence of strings so static checkers see a
                    # consistent type regardless of the concrete collection used
                    # in the bindings module.
                    _sketch_methods = list(SKETCH_CONVENIENCE_METHODS)
                except Exception:
                    _sketch_methods = [
                        'size',
                        'background',
                        'window_title',
                        'no_loop',
                        'loop',
                        'redraw',
                        'save_frame',
                        'rect',
                        'line',
                        'circle',
                        'square',
                        'frame_rate',
                        'fill',
                        'stroke',
                        'stroke_weight',
                        # engine-level helpers
                        'color_mode',
                        # common convenience shims used by examples
                        'rect_mode',
                        'no_cursor',
                        'no_stroke',
                        'no_fill',
                    ]

                for name in _sketch_methods:
                    if hasattr(inst, name):
                        continue
                    # Prefer the API-provided implementation when available
                    fn = None
                    try:
                        fn = getattr(api, name)
                    except Exception:
                        fn = None

                    if fn is not None:
                        try:
                            setattr(inst, name, fn)
                            continue
                        except Exception:
                            # fall through to attempt a fallback
                            pass

                    # Provide tiny, well-scoped fallbacks for essential
                    # helpers so sketches remain usable even if the API
                    # registration or bindings import failed.
                    try:
                        if name == 'size':
                            def _size_fn(w, h):
                                inst._engine._set_size(int(w), int(h))

                            setattr(inst, 'size', _size_fn)
                            continue
                        if name == 'background':
                            def _fb_background(*args, **kwargs):
                                # Try to delegate to core.color if available;
                                # otherwise record a background op with parsed RGB.
                                try:
                                    from core.color.background import set_background
                                    return set_background(inst._engine, *args, **kwargs)
                                except Exception:
                                    try:
                                        # Expect either a single grayscale, or r,g,b
                                        if len(args) == 1:
                                            v = int(args[0])
                                            try:
                                                inst._engine.graphics.record(
                                                    'background', r=v, g=v, b=v
                                                )
                                            except Exception:
                                                pass
                                        else:
                                            r = int(args[0])
                                            g = int(args[1])
                                            b = int(args[2])
                                            try:
                                                inst._engine.graphics.record(
                                                    'background', r=r, g=g, b=b
                                                )
                                            except Exception:
                                                pass
                                    except Exception:
                                        # Best-effort only
                                        pass
                            setattr(inst, 'background', _fb_background)
                            continue
                        if name == 'rect_mode':
                            def _fb_rect_mode(m):
                                try:
                                    inst._engine.rect_mode = str(m)
                                except Exception:
                                    pass
                            setattr(inst, 'rect_mode', _fb_rect_mode)
                            continue
                        if name == 'no_cursor':
                            def _fb_no_cursor():
                                try:
                                    inst._engine._no_cursor = True
                                except Exception:
                                    pass
                            setattr(inst, 'no_cursor', _fb_no_cursor)
                            continue
                        if name == 'no_stroke':
                            def _fb_no_stroke():
                                try:
                                    inst._engine.stroke_color = None
                                except Exception:
                                    pass
                                try:
                                    fn = getattr(inst._engine.api, 'no_stroke')
                                    if callable(fn):
                                        fn()
                                except Exception:
                                    pass
                            setattr(inst, 'no_stroke', _fb_no_stroke)
                            continue
                        if name == 'no_fill':
                            def _fb_no_fill():
                                try:
                                    inst._engine.fill_color = None
                                except Exception:
                                    pass
                                try:
                                    fn = getattr(inst._engine.api, 'no_fill')
                                    if callable(fn):
                                        fn()
                                except Exception:
                                    pass
                            setattr(inst, 'no_fill', _fb_no_fill)
                            continue
                        if name == 'constrain':
                            def _fb_constrain(v, low, high):
                                try:
                                    v_f = float(v)
                                    low_f = float(low)
                                    high_f = float(high)
                                    return max(min(v_f, high_f), low_f)
                                except Exception:
                                    return v
                            setattr(inst, 'constrain', _fb_constrain)
                            continue
                        if name == 'map':
                            def _fb_map(value, start1, stop1, start2, stop2):
                                try:
                                    v = float(value)
                                    s1 = float(start1)
                                    s2 = float(stop1)
                                    t1 = float(start2)
                                    t2 = float(stop2)
                                    if s2 == s1:
                                        raise ValueError('map: start/stop equal')
                                    num = (v - s1) * (t2 - t1)
                                    den = (s2 - s1)
                                    return t1 + num / den
                                except Exception:
                                    return value
                            setattr(inst, 'map', _fb_map)
                            continue
                        if name == 'lerp':
                            def _fb_lerp(a, b, amt):
                                    try:
                                        a_f = float(a)
                                        b_f = float(b)
                                        amt_f = float(amt)
                                        return (1.0 - amt_f) * a_f + amt_f * b_f
                                    except Exception:
                                        return a
                            setattr(inst, 'lerp', _fb_lerp)
                            continue
                        if name == 'norm':
                            def _fb_norm(value, start, stop):
                                try:
                                    v = float(value)
                                    s = float(start)
                                    t = float(stop)
                                    if t == s:
                                        raise ValueError('norm: start==stop')
                                    return (v - s) / (t - s)
                                except Exception:
                                    return 0.0
                            setattr(inst, 'norm', _fb_norm)
                            continue
                        if name == 'round':
                            def _fb_round(v):
                                try:
                                    return round(float(v))
                                except Exception:
                                    try:
                                        return round(v)
                                    except Exception:
                                        return v
                            setattr(inst, 'round', _fb_round)
                            continue
                        if name == 'noise':
                            def _fb_noise(v, *rest):
                                # fallback: use Python's random for smooth-ish output
                                try:
                                    import random as _r
                                    # single-value noise: map random to [0,1]
                                    return float(_r.random())
                                except Exception:
                                    return 0.0
                            setattr(inst, 'noise', _fb_noise)
                            continue
                        if name == 'noise_seed':
                            def _fb_noise_seed(s):
                                try:
                                    import random as _r
                                    _r.seed(int(s))
                                except Exception:
                                    pass
                                return None
                            setattr(inst, 'noise_seed', _fb_noise_seed)
                            continue
                        if name == 'noise_detail':
                            def _fb_noise_detail(lod, falloff=0.5):
                                # noop fallback
                                return None
                            setattr(inst, 'noise_detail', _fb_noise_detail)
                            continue
                        if name == 'random':
                            def _fb_random(*a, **k):
                                try:
                                    from core.random import random as _rand
                                    return _rand(inst._engine, *a)
                                except Exception:
                                    # Last resort: use Python's global random
                                    import random as _r
                                    if len(a) == 0:
                                        return _r.random()
                                    if len(a) == 1:
                                        return _r.random() * float(a[0])
                                    if len(a) == 2:
                                        lo = float(a[0])
                                        hi = float(a[1])
                                        return lo + _r.random() * (hi - lo)
                                    raise TypeError('random() expects 0,1 or 2 args')
                            setattr(inst, 'random', _fb_random)
                            continue
                        if name == 'random_seed':
                            def _fb_random_seed(s):
                                try:
                                    from core.random import random_seed as _rs
                                    return _rs(inst._engine, s)
                                except Exception:
                                    try:
                                        import random as _r
                                        _r.seed(int(s))
                                    except Exception:
                                        pass
                            setattr(inst, 'random_seed', _fb_random_seed)
                            continue
                    except Exception:
                        # If all fallback attempts fail, silently continue; the
                        # absence of the method is preferable to raising
                        # during sketch instantiation.
                        pass
                    try:
                        if name == 'image_mode':
                            def _fb_image_mode(m):
                                try:
                                    inst._engine.image_mode = str(m)
                                except Exception:
                                    pass
                            setattr(inst, 'image_mode', _fb_image_mode)
                            continue
                    except Exception:
                        pass
                    try:
                        if name == 'ellipse_mode':
                            def _fb_ellipse_mode(m):
                                try:
                                    inst._engine.ellipse_mode = str(m)
                                except Exception:
                                    pass
                            setattr(inst, 'ellipse_mode', _fb_ellipse_mode)
                            continue
                    except Exception:
                        pass
                self.sketch = inst
                # Ensure some API helpers that are implemented on SimpleSketchAPI
                # are available as methods on the instance in edge cases where
                # the previous attach logic did not succeed.
                try:
                    if (
                        hasattr(api, 'color_mode')
                        and not hasattr(self.sketch, 'color_mode')
                    ):
                        try:
                            setattr(self.sketch, 'color_mode', api.color_mode)
                        except Exception:
                            pass
                except Exception:
                    pass
            except Exception:
                # fall back to leaving as-is
                pass
        # Note: do NOT auto-instantiate bare classes passed as the sketch
        # module. Tests and examples sometimes pass a class with a free
        # function-style `draw(this)` defined; instantiating would change the
        # call signature (bound method receives `self`). Leave class as-is.

    def step_frame(self):
        """Execute a single frame: call sketch.setup()/draw() and record commands.

        Delegates to `core.engine.frame.step_frame(self)` for the implementation
        but preserves an inline fallback in case the helper cannot be imported.
        """
        try:
            from core.engine.frame import step_frame as _sf
            return _sf(self)
        except Exception:
            # fallback: run the previous inline implementation to preserve
            # behaviour even if the extraction cannot be imported.
            pass
        # Inline fallback (copied from the original implementation)
        # Preserve setup commands (e.g., background) for every frame
        if not hasattr(self, '_setup_commands'):
            self._setup_commands = []
        # On first frame, record setup commands
        if not self._setup_done:
            self.graphics.clear()
            this = SimpleSketchAPI(self)
            setup = getattr(self.sketch, 'setup', None)
            if callable(setup):
                try:
                    self._call_sketch_method(setup, this)
                except Exception:
                    pass
            # Capture and remove any background command emitted in setup so
            # it can be applied once only. Store its RGB for the presenter.
            recorded = list(self.graphics.commands)
            setup_bg = None
            remaining = []
            for cmd in recorded:
                if cmd.get('op') == 'background' and setup_bg is None:
                    args = cmd.get('args', {})
                    r = int(args.get('r', 200))
                    g = int(args.get('g', 200))
                    b = int(args.get('b', 200))
                    setup_bg = (r, g, b)
                else:
                    remaining.append(cmd)
            # store the background captured during setup (or None)
            self._setup_background = setup_bg
            # store setup commands without background so they don't replay each frame
            self._setup_commands = remaining
            self._setup_done = True
            import logging as _logging
            try:
                _logging.getLogger(__name__).debug(
                    'Playing setup commands: %r', self._setup_commands
                )
            except Exception:
                pass
            try:
                _logging.getLogger(__name__).debug(
                    'step_frame: captured setup_background=%r',
                    self._setup_background,
                )
            except Exception:
                pass
        # If no_loop and already drawn, return immediately before any draw logic
        if not self.looping and getattr(self, '_no_loop_drawn', False):
            return
        else:
            self.graphics.clear()
            # Prepend setup commands to graphics.commands for each frame
            self.graphics.commands = list(self._setup_commands)
            # Headless: ensure the first recorded frame contains a background.
            # If the sketch provided a background in setup, that background was
            # captured to `_setup_background` and removed from setup commands to
            # avoid repeating in windowed mode. For headless runs we want the
            # recorded commands to include that background once so snapshots
            # and tests see an initialized canvas.
            if getattr(self, 'headless', False):
                _bg_local = getattr(self, '_setup_background', None)
                if _bg_local is not None and not getattr(
                    self, '_setup_bg_applied_headless', False
                ):
                    bg = _bg_local
                    # prepend background so it appears before other setup commands
                    try:
                        self.graphics.commands.insert(0, {
                            'op': 'background',
                            'args': {
                                'r': int(bg[0]),
                                'g': int(bg[1]),
                                'b': int(bg[2]),
                            },
                            'meta': {'seq': 0},
                        })
                        self._setup_bg_applied_headless = True
                    except Exception:
                        pass
                # Note: do not insert a default background automatically for headless
                # runs. Tests expect recorded command order to reflect only what the
                # sketch emitted. If a default background is desired for snapshots,
                # callers should emit one explicitly.

        # Note: do not auto-insert a default background here. If a sketch
        # wants a background it should call `this.background()` in setup()
        # or draw(). This keeps recorded command order intuitive for tests
        # and user code (drawn shapes appear in the same order they were
        # emitted).
        # Defer calling draw until we've decided whether this frame should run
        # (draw is invoked later once per frame). This avoids accidentally
        # calling draw twice during a single step (which previously caused
        # no_loop sketches to run draw() two times).
        # print("[DEBUG] Engine.step_frame() called. Sketch type:", type(self.sketch))
        # keep track of the sequence id before this frame so we can tag
        # newly-recorded commands with a frame number for debugging
        try:
            start_seq = int(getattr(self.graphics, '_seq', 0))
        except Exception:
            start_seq = 0
        if self.sketch is None:
            import logging as _logging
            try:
                _logging.getLogger(__name__).debug('No sketch attached to engine.')
            except Exception:
                pass
            return

        # (setup is run and recorded earlier in this method; do not run it again)

        # decide whether to run draw this frame
        # Semantics:
        # - If looping is enabled, draw every frame.
        # - If redraw() was requested, draw once.
        # - If no_loop() was called (looping==False) and no redraw() was
        #   requested, do NOT draw. This matches the expectations that
        #   calling no_loop() in setup() prevents any automatic draw.
        should_draw = False
        # If looping is enabled, draw every frame.
        if self.looping:
            should_draw = True
        # If redraw() requested, draw once.
        elif self._redraw_requested:
            should_draw = True
        # If the caller requested we ignore no_loop semantics (for example
        # the CLI --max-frames override), allow drawing even when looping
        # is disabled.
        elif not self.looping and getattr(self, '_ignore_no_loop', False):
            should_draw = True
        # If looping was disabled (no_loop called, e.g. in setup), allow a
        # single one-shot draw on the first frame and then stop. This matches
        # Processing semantics where calling no_loop() prevents continuous
        # looping but still allows one draw to run immediately after setup.
        elif not self.looping and not self._no_loop_drawn and self.frame_count == 0:
            should_draw = True

        if not should_draw:
            return

        # Only call update() then draw() once per frame. update() runs before
        # draw() and can be used to change sketch state (movement, physics,
        # collisions) prior to rendering. Use _call_sketch_method so we
        # gracefully handle both bound methods and module-level functions.
        this = SimpleSketchAPI(self)
        # Call optional update() first
        update_fn = getattr(self.sketch, 'update', None)
        if callable(update_fn):
            try:
                self._call_sketch_method(update_fn, this)
            except Exception:
                # Do not let update errors stop the frame; continue to draw
                pass

        # Then call draw()
        draw = getattr(self.sketch, 'draw', None)
        if callable(draw):
            self._call_sketch_method(draw, this)
        else:
            import logging as _logging
            try:
                _logging.getLogger(__name__).debug('draw is not callable.')
            except Exception:
                pass

        # Tag any commands recorded during this step with the current frame index
        try:
            for cmd in self.graphics.commands:
                meta = cmd.setdefault('meta', {})
                seq = int(meta.get('seq', 0))
                if seq > start_seq:
                    meta['frame'] = int(self.frame_count)
        except Exception:
            pass

        # reset one-shot redraw request
        if self._redraw_requested:
            self._redraw_requested = False

        # If looping is disabled and we are NOT ignoring no_loop, mark that
        # we've run the one-shot draw so subsequent frames are skipped early.
        if not self.looping and not getattr(self, '_ignore_no_loop', False):
            self._no_loop_drawn = True

        self.frame_count += 1

    def _call_sketch_method(self, fn: Callable, this: SimpleSketchAPI):
        """Delegate to event_dispatch.call_sketch_method for handler invocation."""
        try:
            from core.engine.event_dispatch import call_sketch_method as _csm
            return _csm(fn, this)
        except Exception:
            try:
                bound_self = getattr(fn, '__self__', None)
                if bound_self is not None:
                    return fn()
            except Exception:
                pass
            try:
                return fn(this)
            except TypeError:
                return fn()

    def run_frames(self, n: int = 1, ignore_no_loop: bool = False):
        import time
        # Temporarily set a flag so step_frame can observe whether the
        # caller asked to ignore no_loop semantics for this run.
        prev_ignore = getattr(self, '_ignore_no_loop', False)
        self._ignore_no_loop = bool(ignore_no_loop)

        frame_counter = 0
        while frame_counter < n:
            # Stop if no_loop has already drawn, unless caller requested we
            # ignore no_loop semantics (for example, CLI --max-frames override).
            if (
                not getattr(self, '_ignore_no_loop', False)
                and not self.looping
                and getattr(self, '_no_loop_drawn', False)
            ):
                break
            start = time.perf_counter()
            self.step_frame()
            # verbose output: print recorded commands after each frame
            if getattr(self, '_verbose', False):
                for cmd in self.graphics.commands:
                    try:
                        print('VERBOSE CMD:', cmd)
                    except Exception:
                        pass
            # enforce frame rate if requested and running in non-headless mode
            if self.frame_rate > 0 and not self.headless:
                elapsed = time.perf_counter() - start
                target = 1.0 / float(self.frame_rate)
                to_sleep = target - elapsed
                if to_sleep > 0:
                    time.sleep(to_sleep)
            frame_counter += 1
        # restore previous flag
        self._ignore_no_loop = prev_ignore

    # Windowed lifecycle helpers
    def start(self, max_frames: Optional[int] = None):
        """Start a windowed run of the sketch. If headless, behave like run_frames.

        When not headless, this creates a pyglet window and schedules frame
        updates at the chosen frame_rate. If max_frames is provided, the app
        will exit after that many frames.
        """
        if self.headless:
            # emulate windowed start in headless mode
            if max_frames is None:
                self.run_frames(1)
            else:
                # If caller provided max_frames, honor it even if the sketch
                # requests no_loop(). This mirrors the CLI semantics where
                # --max-frames should run the requested number of frames.
                self.run_frames(max_frames, ignore_no_loop=True)
            return

        # Lazy-import pyglet to avoid import-time dependency in tests
        try:
            import pyglet
        except Exception as exc:  # pragma: no cover - platform specific
            raise RuntimeError('pyglet is required for windowed mode') from exc
        # Setup is now handled in step_frame; do not run it here

        # create window using potentially updated size from setup()
        # Ensure `setup()` runs at least once before creating the window so
        # that any setup-time background is captured. Pyglet may invoke
        # `on_draw` immediately after window creation which can race with
        # scheduled updates; running setup here avoids that race.
        if not getattr(self, '_setup_done', False):
            try:
                # Run setup and capture setup commands similar to step_frame()
                self.graphics.clear()
                this = SimpleSketchAPI(self)
                setup = getattr(self.sketch, 'setup', None)
                if callable(setup):
                    self._call_sketch_method(setup, this)
                recorded = list(self.graphics.commands)
                setup_bg = None
                remaining = []
                for cmd in recorded:
                    if cmd.get('op') == 'background' and setup_bg is None:
                        args = cmd.get('args', {})
                        r = int(args.get('r', 200))
                        g = int(args.get('g', 200))
                        b = int(args.get('b', 200))
                        setup_bg = (r, g, b)
                    else:
                        remaining.append(cmd)
                self._setup_background = setup_bg
                self._setup_commands = remaining
                self._setup_done = True
            except Exception:
                pass
        # Creating a pyglet window on macOS sometimes prints ObjC callback
        # exceptions during teardown even though the app continues to run.
        # Temporarily redirect stderr to hide that noise while still
        # propagating real failures.
        try:
            devnull = open(os.devnull, 'w')
            with redirect_stderr(devnull):
                # Create window; cast to Any for static checking so mypy
                # does not attempt to verify pyglet's internal abstract base
                # classes here.
                from typing import Any as _Any
                from typing import cast
                # create window with explicit keyword args broken across lines
                _win = pyglet.window.Window(
                    width=self.width, height=self.height, vsync=True
                )
                # cast to Any to avoid mypy attempting to validate pyglet's
                # abstract base classes in this context.
                self._window = cast(_Any, _win)
        finally:
            try:
                devnull.close()
            except Exception:
                pass

        # Some test harnesses provide a lightweight Dummy window that does not
        # implement pyglet's `@window.event` decorator. Provide a best-effort
        # fallback that emulates an `.event` decorator by attaching the
        # function to the window object under the function name. This keeps
        # tests that monkeypatch `pyglet.window.Window` from erroring on
        # attribute access.
        try:
            if not hasattr(self._window, 'event'):
                def _event_decorator(fn):
                    # attach as an attribute so callers can still access it
                    try:
                        setattr(self._window, fn.__name__, fn)
                    except Exception:
                        pass
                    return fn

                try:
                    setattr(self._window, 'event', _event_decorator)
                except Exception:
                    pass
        except Exception:
            pass
        # Apply any window title requested during setup()/before the window
        # existed. This ensures calls to this.window_title(...) in setup are
        # persisted and applied once the window is available.
        try:
            pending = getattr(self, '_pending_window_title', None)
            if pending is not None:
                try:
                    self._window.set_caption(str(pending))
                except Exception:
                    pass
        except Exception:
            pass
        try:
            # Keep the debug print short to satisfy linters.
            s = 'size=({}, {})'.format(self.width, self.height)
            print('Engine: created window', self._window, s)
        except Exception:
            pass
        # running until the user explicitly closes the window.
        self._frames_left = float(
            'inf') if max_frames is None else int(max_frames)

        # Create presenter once so the underlying FBO/texture and Skia surface
        # persist across frames. Delegate windowed loop wiring and scheduling
        # to `core.engine.loop.setup_window_loop` so `impl.py` stays small.
        from typing import Any as _Any
        from core.engine.presenter import create_presenter
        from core.engine.loop import setup_window_loop

        presenter: _Any = create_presenter(
            SkiaGLPresenter,
            self.width,
            self.height,
            present_mode=self.present_mode,
            force_gles=self.force_gles,
        )
        # Persist presenter onto the engine so other helpers (e.g. save_frame)
        # can access the presenter's backing surface for accurate screen
        # captures when running windowed.
        try:
            setattr(self, '_presenter', presenter)
        except Exception:
            pass
        # Debug: record which presenter class was instantiated so we can
        # verify whether SkiaGLPresenter or a fallback is being used.
        try:
            if os.getenv('PYCREATIVE_DEBUG_PRESENT', '') == '1':
                try:
                    print(f'Engine: presenter type={presenter.__class__.__name__}')
                except Exception:
                    pass
                try:
                    with open('/tmp/pycreative_present_class.txt', 'a') as _f:
                        _f.write(f'{presenter.__class__.__name__}\n')
                except Exception:
                    pass
        except Exception:
            pass

        # Delegate the remaining windowed setup, event handler registration
        # and scheduling to the extracted helper. It may call pyglet.app.run()
        # and return True to indicate it ran the app loop. If it did, avoid
        # duplicating scheduling/run logic below.
        # Delegate windowed setup, event handler registration and scheduling
        # to the extracted helper. The helper may run the app loop and will
        # return True to indicate it did so. If it ran the loop, return
        # early so we don't schedule/run a second app loop here.
        try:
            ran_app = False
            try:
                ran_app = bool(setup_window_loop(self, presenter, max_frames=max_frames))
            except Exception:
                ran_app = False
            if ran_app:
                # The helper handled the run and teardown; finish start().
                return
        except Exception:
            # Best-effort only: if loop wiring fails, continue to scheduling
            # and running below so the engine still attempts to run.
            pass

        # Note: we intentionally avoid creating a pyglet Image backed by
        # the presenter's GL texture. Wrapping an external GL texture in a
        # pyglet.image.Texture can cause GL_INVALID_OPERATION depending on
        # driver/context state. The presenter.present() implementation
        # performs the direct GL textured-quad draw and is the preferred
        # display path.

        # whether start() was given an explicit max_frames (in which case
        # we should ignore sketch no_loop semantics for the duration of this
        # run)
        self._ignore_no_loop = False if max_frames is None else True

        def update(dt):
            # Stop if no_loop has already drawn unless we're explicitly
            # ignoring no_loop for this run.
            if (
                not self._ignore_no_loop
                and not self.looping
                and getattr(self, '_no_loop_drawn', False)
            ):
                return
            # debug: Engine.update() called (dt, frames_left)
            self.step_frame()
            # verbose: echo recorded commands to stdout for debugging
            if getattr(self, '_verbose', False):
                for cmd in self.graphics.commands:
                    try:
                        print('VERBOSE CMD:', cmd)
                    except Exception:
                        pass
            # request a redraw
            try:
                self._window.invalid = True
            except Exception:
                pass
            # decrement frame counter and exit when done
            if self._frames_left is not None:
                self._frames_left -= 1
                if self._frames_left <= 0:
                    try:
                        self._window.close()
                    except Exception:
                        pass
                    import pyglet
                    pyglet.app.exit()

        # schedule updates at frame_rate if set, otherwise use default clock tick
        interval = None if self.frame_rate < 1 else 1.0 / \
            float(self.frame_rate)
        if interval is None:
            pyglet.clock.schedule(update)
            try:
                print('Engine: scheduled update (unspecified interval)')
            except Exception:
                pass
        else:
            pyglet.clock.schedule_interval(update, interval)
            try:
                print(f'Engine: scheduled update interval={interval}s')
            except Exception:
                pass

        # run the app (blocks until exit). Suppress noisy stderr messages from
        # the platform/pyglet bridge while still allowing the app to run.
        try:
            print('Engine: entering pyglet.app.run()')
        except Exception:
            pass
        try:
            devnull = open(os.devnull, 'w')
            with redirect_stderr(devnull):
                pyglet.app.run()
        finally:
            try:
                devnull.close()
            except Exception:
                pass
        try:
                if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                    try:
                        import logging
                        import threading
                        logger = logging.getLogger(__name__)
                        ths = threading.enumerate()
                        logger.debug('threads after pyglet.app.run returned:')
                        for t in ths:
                            try:
                                logger.debug('  %s daemon=%s', t.name, t.daemon)
                            except Exception:
                                pass
                    except Exception:
                        pass
        except Exception:
            pass
        try:
            print('Engine: pyglet.app.run() returned')
        except Exception:
            pass

    def stop(self):
        """Stop a running window (if any)."""
        try:
            import pyglet
            pyglet.app.exit()
        except Exception:
            pass

    # Engine-side helpers used by SimpleSketchAPI
    def _set_size(self, w: int, h: int):
        """Set engine size and resize the window if one exists.

        This should be safe to call in headless mode (no-op for window). If a
        pyglet window exists, call its set_size method and update the GL
        viewport where possible so rendering matches the new size.
        """
        self.width = int(w)
        self.height = int(h)
        # If a window exists, resize it and try to update GL viewport.
        win = getattr(self, '_window', None)
        if win is not None:
            try:
                win.set_size(self.width, self.height)
            except Exception:
                # Some window implementations may not support set_size; ignore.
                pass
            # Attempt to update GL viewport if pyglet.gl is available
            try:
                from pyglet import gl
                gl.glViewport(0, 0, int(self.width), int(self.height))
            except Exception:
                pass

    def _no_loop(self):
        self.looping = False

    def _loop(self):
        self.looping = True

    def _redraw(self):
        self._redraw_requested = True

    def _save_frame(self, path: str):
        """Save a placeholder snapshot for headless mode. If Pillow is
        available, write a simple PNG. Otherwise, record the request.
        """
        try:
            from core.engine.snapshot import save_frame as _save
            return _save(self, path)
        except Exception:
            # As a very last resort, record the request without writing
            try:
                self.graphics.record('save_frame', path=path, backend='none')
            except Exception:
                pass

    # --- Mouse/input simulation helpers ---------------------------------
    def _ensure_setup(self):
        """Ensure setup() has run on the sketch. If not, run a single frame
        which will execute setup() and capture any setup commands.
        """
        if not getattr(self, '_setup_done', False):
            # run a single frame in headless mode to execute setup
            try:
                self.run_frames(1)
            except Exception:
                # best-effort only
                pass

    def _apply_mouse_update(self, x: Optional[int], y: Optional[int]):
        """Delegate mouse coordinate updates to input_simulation helper."""
        try:
            from core.engine.input_simulation import _apply_mouse_update as _iu
            return _iu(self, x, y)
        except Exception:
            # Fallback: preserve previous behaviour inline
            try:
                self.pmouse_x = int(self.mouse_x)
            except Exception:
                self.pmouse_x = 0
            try:
                self.pmouse_y = int(self.mouse_y)
            except Exception:
                self.pmouse_y = 0
            if x is not None:
                try:
                    self.mouse_x = int(x)
                except Exception:
                    pass
            if y is not None:
                try:
                    self.mouse_y = int(y)
                except Exception:
                    pass

    def simulate_mouse_press(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: Optional[str] = None,
        event: Optional[object] = None,
    ):
        """Delegate to input_simulation.simulate_mouse_press."""
        try:
            from core.engine.input_simulation import simulate_mouse_press as _sp
            return _sp(self, x=x, y=y, button=button, event=event)
        except Exception:
            # fallback: run inline to preserve behaviour
            pass

    def simulate_mouse_release(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: Optional[str] = None,
        event: Optional[object] = None,
    ):
        """Delegate to input_simulation.simulate_mouse_release."""
        try:
            from core.engine.input_simulation import simulate_mouse_release as _sr
            return _sr(self, x=x, y=y, button=button, event=event)
        except Exception:
            pass

    def simulate_mouse_move(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        event: Optional[object] = None,
    ):
        """Delegate to input_simulation.simulate_mouse_move."""
        try:
            from core.engine.input_simulation import simulate_mouse_move as _sm
            return _sm(self, x=x, y=y, event=event)
        except Exception:
            pass

    def simulate_mouse_drag(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: Optional[str] = None,
        event: Optional[object] = None,
    ):
        """Delegate to input_simulation.simulate_mouse_drag."""
        try:
            from core.engine.input_simulation import simulate_mouse_drag as _sd
            return _sd(self, x=x, y=y, button=button, event=event)
        except Exception:
            pass

    def simulate_mouse_wheel(self, event_or_count: object):
        """Delegate to input_simulation.simulate_mouse_wheel."""
        try:
            from core.engine.input_simulation import simulate_mouse_wheel as _sw
            return _sw(self, event_or_count)
        except Exception:
            pass

    def simulate_key_press(
        self,
        key: Optional[str] = None,
        key_code: Optional[str] = None,
        event: Optional[object] = None,
    ):
        """Delegate to input_simulation.simulate_key_press."""
        try:
            from core.engine.input_simulation import simulate_key_press as _kp
            return _kp(self, key=key, key_code=key_code, event=event)
        except Exception:
            pass

    def simulate_key_release(
        self,
        key: Optional[str] = None,
        key_code: Optional[str] = None,
        event: Optional[object] = None,
    ):
        """Delegate to input_simulation.simulate_key_release."""
        try:
            from core.engine.input_simulation import simulate_key_release as _kr
            return _kr(self, key=key, key_code=key_code, event=event)
        except Exception:
            pass


    # --- 2D Transform / matrix stack helpers ----------------------------
    def _identity_matrix(self):
        """Delegate to transforms.identity_matrix()."""
        try:
            from core.engine.transforms import identity_matrix as _id
            return _id()
        except Exception:
            return [1.0, 0.0, 0.0,
                    0.0, 1.0, 0.0,
                    0.0, 0.0, 1.0]

    def _mul_mat(self, a, b):
        """Delegate to transforms.mul_mat(a, b)."""
        try:
            from core.engine.transforms import mul_mat as _mul
            return _mul(a, b)
        except Exception:
            return [
                a[0]*b[0] + a[1]*b[3] + a[2]*b[6],
                a[0]*b[1] + a[1]*b[4] + a[2]*b[7],
                a[0]*b[2] + a[1]*b[5] + a[2]*b[8],

                a[3]*b[0] + a[4]*b[3] + a[5]*b[6],
                a[3]*b[1] + a[4]*b[4] + a[5]*b[7],
                a[3]*b[2] + a[4]*b[5] + a[5]*b[8],

                a[6]*b[0] + a[7]*b[3] + a[8]*b[6],
                a[6]*b[1] + a[7]*b[4] + a[8]*b[7],
                a[6]*b[2] + a[7]*b[5] + a[8]*b[8],
            ]

    def _ensure_matrix_stack(self):
        try:
            from core.engine.transforms import ensure_matrix_stack as _ems
            return _ems(self)
        except Exception:
            if not hasattr(self, '_matrix_stack'):
                self._matrix_stack = [self._identity_matrix()]

    def push_matrix(self):
        try:
            from core.engine.transforms import push_matrix as _pm
            return _pm(self)
        except Exception:
            self._ensure_matrix_stack()
            try:
                top = list(self._matrix_stack[-1])
                self._matrix_stack.append(top)
            except Exception:
                self._matrix_stack = [self._identity_matrix()]
            try:
                return self.graphics.record('push_matrix')
            except Exception:
                return None

    def pop_matrix(self):
        try:
            from core.engine.transforms import pop_matrix as _pop
            return _pop(self)
        except Exception:
            self._ensure_matrix_stack()
            try:
                if len(self._matrix_stack) > 1:
                    self._matrix_stack.pop()
                else:
                    self._matrix_stack[-1] = self._identity_matrix()
            except Exception:
                self._matrix_stack = [self._identity_matrix()]
            try:
                return self.graphics.record('pop_matrix')
            except Exception:
                return None

    def reset_matrix(self):
        try:
            from core.engine.transforms import reset_matrix as _rm
            return _rm(self)
        except Exception:
            self._ensure_matrix_stack()
            try:
                self._matrix_stack[-1] = self._identity_matrix()
            except Exception:
                self._matrix_stack = [self._identity_matrix()]
            try:
                return self.graphics.record('reset_matrix')
            except Exception:
                return None

    def _apply_transform_matrix(self, mat):
        """Delegate to transforms.apply_transform_matrix."""
        try:
            from core.engine.transforms import apply_transform_matrix as _atm
            return _atm(self, mat)
        except Exception:
            self._ensure_matrix_stack()
            try:
                cur = self._matrix_stack[-1]
                self._matrix_stack[-1] = self._mul_mat(cur, mat)
            except Exception:
                self._matrix_stack[-1] = list(mat)

    def translate(self, x: float, y: float, z: Optional[float] = None):
        try:
            from core.engine.transforms import translate as _t
            return _t(self, x, y)
        except Exception:
            try:
                tx = float(x)
                ty = float(y)
            except Exception:
                return None
            mat = [1.0, 0.0, tx,
                   0.0, 1.0, ty,
                   0.0, 0.0, 1.0]
            self._apply_transform_matrix(mat)
            try:
                return self.graphics.record('translate', x=tx, y=ty)
            except Exception:
                return None

    def rotate(self, angle: float):
        try:
            from core.engine.transforms import rotate as _r
            return _r(self, angle)
        except Exception:
            import math
            try:
                a = float(angle)
            except Exception:
                return None
            c = math.cos(a)
            s = math.sin(a)
            mat = [c, -s, 0.0,
                   s,  c, 0.0,
                   0.0,0.0,1.0]
            self._apply_transform_matrix(mat)
            try:
                return self.graphics.record('rotate', angle=float(a))
            except Exception:
                return None

    def scale(self, sx: float, sy: Optional[float] = None, sz: Optional[float] = None):
        try:
            from core.engine.transforms import scale as _s
            return _s(self, sx, sy)
        except Exception:
            try:
                sx_f = float(sx)
                sy_f = float(sy) if sy is not None else sx_f
            except Exception:
                return None
            mat = [sx_f, 0.0, 0.0,
                   0.0, sy_f, 0.0,
                   0.0, 0.0, 1.0]
            self._apply_transform_matrix(mat)
            try:
                return self.graphics.record('scale', sx=sx_f, sy=sy_f)
            except Exception:
                return None

    def shear_x(self, angle: float):
        try:
            from core.engine.transforms import shear_x as _sx
            return _sx(self, angle)
        except Exception:
            import math
            try:
                a = float(angle)
            except Exception:
                return None
            mat = [1.0, math.tan(a), 0.0,
                   0.0, 1.0,        0.0,
                   0.0, 0.0,        1.0]
            self._apply_transform_matrix(mat)
            try:
                return self.graphics.record('shear_x', angle=float(a))
            except Exception:
                return None

    def shear_y(self, angle: float):
        try:
            from core.engine.transforms import shear_y as _sy
            return _sy(self, angle)
        except Exception:
            import math
            try:
                a = float(angle)
            except Exception:
                return None
            mat = [1.0, 0.0,        0.0,
                   math.tan(a), 1.0, 0.0,
                   0.0, 0.0,        1.0]
            self._apply_transform_matrix(mat)
            try:
                return self.graphics.record('shear_y', angle=float(a))
            except Exception:
                return None

    def apply_matrix(self, *args):
        """Delegate to transforms.apply_matrix."""
        try:
            from core.engine.transforms import apply_matrix as _am
            return _am(self, *args)
        except Exception:
            vals = None
            if len(args) == 1:
                maybe = args[0]
                try:
                    vals = list(maybe)
                except Exception:
                    vals = None
            else:
                vals = list(args)

            if vals is None:
                return None

        try:
            if len(vals) == 6:
                # assume [a,b,c,d,e,f] -> 3x3: [a,b,c, d,e,f, 0,0,1]
                mat = [float(vals[0]), float(vals[1]), float(vals[2]),
                       float(vals[3]), float(vals[4]), float(vals[5]),
                       0.0, 0.0, 1.0]
                self._apply_transform_matrix(mat)
            elif len(vals) == 9:
                mat = [float(v) for v in vals]
                self._apply_transform_matrix(mat)
            elif len(vals) == 16:
                # Accept 4x4 matrix (row-major). For 2D engine we won't
                # attempt a full 4x4 -> 3x3 conversion; just record values
                # so headless tests can observe the call. Do not modify
                # the engine matrix stack for 4x4 inputs.
                mat = [float(v) for v in vals]
            else:
                return None
        except Exception:
            return None

        try:
            return self.graphics.record('apply_matrix', matrix=mat)
        except Exception:
            return None
