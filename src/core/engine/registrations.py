"""Small helpers to keep Engine.__init__ lean: register shape and random APIs.

This module centralizes third-party or optional API registrations so the
main Engine implementation stays compact and easier to review.
"""
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core._types import EngineProtocol as Engine


def register_shape_apis(engine: 'Engine'):
    # Import the shape module and look up functions by name at runtime.
    # This avoids mypy/static-import complaints when optional helpers
    # (like `ellipse`) are not present in the module.
    try:
        import core.shape as _shape
        if hasattr(_shape, 'rect'):
            engine.api.register('rect', lambda *a, **k: getattr(_shape, 'rect')(engine, *a, **k))
        if hasattr(_shape, 'line'):
            engine.api.register('line', lambda *a, **k: getattr(_shape, 'line')(engine, *a, **k))
        if hasattr(_shape, 'point'):
            engine.api.register('point', lambda *a, **k: getattr(_shape, 'point')(engine, *a, **k))

        # optional helpers
        if hasattr(_shape, 'circle'):
            engine.api.register('circle', lambda *a, **k: getattr(_shape, 'circle')(engine, *a, **k))
        if hasattr(_shape, 'ellipse'):
            engine.api.register('ellipse', lambda *a, **k: getattr(_shape, 'ellipse')(engine, *a, **k))
        # expose shape recording helpers so sketches can call begin_shape/vertex/end_shape
        if hasattr(_shape, 'begin_shape'):
            engine.api.register('begin_shape', lambda *a, **k: getattr(_shape, 'begin_shape')(engine, *a, **k))
        if hasattr(_shape, 'vertex'):
            engine.api.register('vertex', lambda *a, **k: getattr(_shape, 'vertex')(engine, *a, **k))
        if hasattr(_shape, 'end_shape'):
            engine.api.register('end_shape', lambda *a, **k: getattr(_shape, 'end_shape')(engine, *a, **k))
    except Exception:
        # best-effort only
        pass


def register_random_and_noise(engine: 'Engine'):
    try:
        from core.random import (
            random as _rand,
        )
        from core.random import (
            random_gaussian as _rand_gauss,
        )
        from core.random import (
            random_seed as _rand_seed,
        )
        from core.random import (
            uniform as _rand_uniform,
        )
        engine.api.register('random', lambda *a, **k: _rand(engine, *a, **k))
        engine.api.register('random_seed', lambda *a, **k: _rand_seed(engine, *a, **k))
        try:
            engine.api.register('random_gaussian', lambda *a, **k: _rand_gauss(engine, *a, **k))
        except Exception:
            pass
        try:
            engine.api.register('uniform', lambda *a, **k: _rand_uniform(engine, *a, **k))
        except Exception:
            pass
        # noise family
        try:
            from core.random import noise as _noise
            from core.random import noise_detail as _noise_detail
            from core.random import noise_seed as _noise_seed
            engine.api.register('noise', lambda *a, **k: _noise(engine, *a, **k))
            engine.api.register('noise_seed', lambda *a, **k: _noise_seed(engine, *a, **k))
            engine.api.register('noise_detail', lambda *a, **k: _noise_detail(engine, *a, **k))
        except Exception:
            pass
    except Exception:
        pass


def register_math(engine: 'Engine'):
    """Expose the small core.math helpers via the engine API so sketches
    can access them as `self.sin`, `self.cos`, `self.radians`, etc.
    """
    try:
        import core.math as _m
        # Register a small subset commonly used in sketches
        for name in ('sin', 'cos', 'tan', 'radians', 'degrees', 'sqrt', 'pow', 'abs_', 'floor', 'ceil'):
            if hasattr(_m, name):
                # Normalize names: core.math uses names like abs_ and map_
                target_name = name.rstrip('_')
                engine.api.register(target_name, lambda *a, _n=name, **k: getattr(_m, _n)(*a, **k))
    except Exception:
        pass


def register_state_apis(engine: 'Engine'):
    """Register simple color and stroke related APIs on the engine.

    These functions mutate engine state (fill_color, stroke_color,
    stroke_weight) and record corresponding graphics commands so sketches
    that call `fill()`, `stroke()`, etc continue to work in headless
    mode.
    """
    try:
        def _rec_fill(rgba):
            engine.fill_color = tuple(int(x) for x in rgba)
            g = getattr(engine, 'graphics', None)
            if g is not None:
                try:
                    return g.record('fill', color=engine.fill_color, fill_alpha=getattr(engine, 'fill_alpha', None))
                except Exception:
                    return None
            return None

        def _rec_stroke(rgba):
            engine.stroke_color = tuple(int(x) for x in rgba)
            g = getattr(engine, 'graphics', None)
            if g is not None:
                try:
                    return g.record('stroke', color=engine.stroke_color, stroke_alpha=getattr(engine, 'stroke_alpha', None))
                except Exception:
                    return None
            return None

        def _rec_no_fill():
            engine.fill_color = None
            g = getattr(engine, 'graphics', None)
            if g is not None:
                try:
                    return g.record('no_fill')
                except Exception:
                    return None
            return None

        def _rec_no_stroke():
            engine.stroke_color = None
            g = getattr(engine, 'graphics', None)
            if g is not None:
                try:
                    return g.record('no_stroke')
                except Exception:
                    return None
            return None

        def _rec_stroke_weight(w):
            engine.stroke_weight = int(w)
            g = getattr(engine, 'graphics', None)
            if g is not None:
                try:
                    return g.record('stroke_weight', weight=int(w))
                except Exception:
                    return None
            return None

        def _rec_stroke_cap(cap):
            try:
                engine.stroke_cap = cap
            except Exception:
                pass
            g = getattr(engine, 'graphics', None)
            if g is not None:
                try:
                    return g.record('stroke_cap', cap=cap)
                except Exception:
                    return None
            return None

        def _rec_stroke_join(join):
            try:
                engine.stroke_join = join
            except Exception:
                pass
            g = getattr(engine, 'graphics', None)
            if g is not None:
                try:
                    return g.record('stroke_join', join=join)
                except Exception:
                    return None
            return None

        try:
            engine.api.register('fill', _rec_fill)
            engine.api.register('stroke', _rec_stroke)
            engine.api.register('stroke_weight', _rec_stroke_weight)
            # register cap/join recorders so sketches calling stroke_cap()/stroke_join()
            # during setup record the current state into the graphics buffer.
            try:
                engine.api.register('stroke_cap', _rec_stroke_cap)
                engine.api.register('stroke_join', _rec_stroke_join)
            except Exception:
                pass
            try:
                engine.api.register('no_fill', lambda *a, **k: _rec_no_fill())
                engine.api.register('no_stroke', lambda *a, **k: _rec_no_stroke())
            except Exception:
                pass
        except Exception:
            pass
        # Expose save_frame to sketches (delegates to engine snapshot orchestration)
        try:
            from core.engine.snapshot import save_frame as _save_fn

            def _save_wrapper(*a, **k) -> None:
                # requested path (positional or keyword)
                p = a[0] if a else k.get('path', None)
                try:
                    import sys as _sys
                    print(f"[Engine.save_frame] sketch requested save_frame path={p} headless={getattr(engine,'headless',None)}")
                    try:
                        print(f"[Engine.save_frame] sketch requested save_frame path={p} headless={getattr(engine,'headless',None)}", file=_sys.stderr)
                    except Exception:
                        pass
                except Exception:
                    pass

                try:
                    setattr(engine, '_last_save_frame_debug', {'requested': p})
                except Exception:
                    pass

                # Call the core snapshot orchestration
                from typing import Any
                res: Any = None
                try:
                    _save_fn(engine, *a, **k)
                except Exception:
                    try:
                        _save_fn(engine, *a, **k)
                    except Exception:
                        res = None

                # If the snapshot orchestration queued the request for the
                # presenter, it will live in engine._pending_save_frames.
                # Detect that and print a helpful message so callers know the
                # write is deferred until the presenter processes pending ops.
                try:
                    pending_list = getattr(engine, '_pending_save_frames', None)
                    if pending_list:
                        try:
                            import sys as _sys
                            print(f"[Engine.save_frame] save_frame queued for presenter (pending count={len(pending_list)}) path={p}")
                            try:
                                print(f"[Engine.save_frame] save_frame queued for presenter (pending count={len(pending_list)}) path={p}", file=_sys.stderr)
                            except Exception:
                                pass
                        except Exception:
                            pass
                except Exception:
                    pass

                # Inspect recorded graphics commands for resolved path/backend
                try:
                    g = getattr(engine, 'graphics', None)
                    if g is not None:
                        cmds = getattr(g, 'commands', None) or []
                        for cmd in reversed(cmds):
                            if cmd.get('op') == 'save_frame':
                                args = cmd.get('args') or {}
                                rp = args.get('path')
                                backend = args.get('backend')
                                try:
                                    import sys as _sys
                                    print(f"[Engine.save_frame] resolved path={rp} backend={backend}")
                                    try:
                                        print(f"[Engine.save_frame] resolved path={rp} backend={backend}", file=_sys.stderr)
                                    except Exception:
                                        pass
                                except Exception:
                                    pass
                                try:
                                    import logging as _logging
                                    _logging.getLogger('pycreative.engine.save_frame').info('resolved save_frame path=%s backend=%s', rp, backend)
                                except Exception:
                                    pass
                                try:
                                    prev = getattr(engine, '_last_save_frame_debug', {}) or {}
                                    prev.update({'resolved': rp, 'backend': backend})
                                    setattr(engine, '_last_save_frame_debug', prev)
                                except Exception:
                                    pass
                                break
                except Exception:
                    pass

                return res

            engine.api.register('save_frame', _save_wrapper)
        except Exception:
            pass
        # Expose color_mode so sketches can switch between RGB/HSB and
        # provide optional maxima (e.g., color_mode('HSB', 360, 100, 100)).
        try:
            def _set_color_mode(mode, *maxs):
                try:
                    mstr = str(mode).upper()
                except Exception:
                    mstr = 'RGB'
                try:
                    setattr(engine, 'color_mode', mstr)
                except Exception:
                    pass
                # store optional maxima for HSB conversions
                try:
                    if maxs:
                        setattr(engine, 'color_mode_max', tuple(maxs))
                    else:
                        setattr(engine, 'color_mode_max', None)
                except Exception:
                    try:
                        setattr(engine, 'color_mode_max', None)
                    except Exception:
                        pass
                return None

            engine.api.register('color_mode', _set_color_mode)
        except Exception:
            pass
        # Expose small color helpers (pure ops) so sketches can query
        # components and HSB values via `self.red(self_color)` or
        # `self.hue(self_color)` etc. These are pure functions in
        # core.color and safe to attach as API helpers.
        try:
            from core.color import red as _red, green as _green, blue as _blue, alpha as _alpha, rgb_to_hsb as _rgb_to_hsb, color as _color_fn, lerp_color as _lerp_color
            # hsb->rgb helper for color-mode-aware color() wrapper
            from typing import Optional, Callable
            _hsb_to_rgb_fn: Optional[Callable[[float, float, float], tuple[int, int, int]]] = None
            try:
                from core.color import hsb_to_rgb as _hsb_to_rgb_fn
            except Exception:
                pass

            # Support color inputs as either a packed ARGB int (legacy
            # core.color.ops API) or an (r,g,b) or (r,g,b,a) tuple/list
            # returned by `PCImage.get()` / Pillow. Normalize to r,g,b ints
            # before delegating to pure helpers.
            def _unpack_rgb(c):
                # None or missing pixel -> treat as black
                if c is None:
                    return 0, 0, 0
                # Packed int path
                try:
                    if isinstance(c, int):
                        return int(_red(c)), int(_green(c)), int(_blue(c))
                except Exception:
                    pass
                # Tuple/list path: accept (r,g,b) or (r,g,b,a)
                try:
                    if isinstance(c, (tuple, list)) and len(c) >= 3:
                        r = c[0]
                        g = c[1]
                        b = c[2]
                        # Some callers may supply floats in 0..1 range; scale
                        # up if values look fractional.
                        def _scale_if_frac(v):
                            try:
                                fv = float(v)
                                if 0.0 <= fv <= 1.0:
                                    return int(round(fv * 255.0))
                                return int(round(fv))
                            except Exception:
                                try:
                                    return int(v)
                                except Exception:
                                    return 0

                        return _scale_if_frac(r), _scale_if_frac(g), _scale_if_frac(b)
                except Exception:
                    pass
                # Fallback: unknown format -> treat as black rather than
                # raising so sorting/rendering remains robust when image
                # pixels are missing or malformed.
                return 0, 0, 0

            def _red_wrap(c):
                r, g, b = _unpack_rgb(c)
                return float(r)

            def _green_wrap(c):
                r, g, b = _unpack_rgb(c)
                return float(g)

            def _blue_wrap(c):
                r, g, b = _unpack_rgb(c)
                return float(b)

            def _alpha_wrap(c):
                # If input is packed int, use core helper; if tuple, try index 3
                try:
                    if isinstance(c, int):
                        return float(_alpha(c))
                except Exception:
                    pass
                try:
                    if isinstance(c, (tuple, list)) and len(c) >= 4:
                        a = c[3]
                        af = float(a)
                        if af <= 1.0:
                            return af * 255.0
                        return af
                except Exception:
                    pass
                return 255.0

            engine.api.register('red', lambda *a, **k: _red_wrap(a[0] if a else None))
            engine.api.register('green', lambda *a, **k: _green_wrap(a[0] if a else None))
            engine.api.register('blue', lambda *a, **k: _blue_wrap(a[0] if a else None))
            engine.api.register('alpha', lambda *a, **k: _alpha_wrap(a[0] if a else None))
            # Register a color() wrapper that respects engine.color_mode and
            # engine.color_mode_max when the sketch uses HSB mode. The pure
            # core.color.color() helper is unaware of engine state and
            # treats arguments as raw numbers; Processing's color() is
            # affected by colorMode(), so we emulate that behavior here.
            def _color_wrapper(*args):
                try:
                    mode = getattr(engine, 'color_mode', 'RGB')
                except Exception:
                    mode = 'RGB'
                maxs = getattr(engine, 'color_mode_max', None)
                # If in HSB mode and we have the hsb->rgb helper,
                # convert h,s,b(,a) -> r,g,b(,a) using the configured maxima.
                if str(mode).upper() == 'HSB' and _hsb_to_rgb_fn is not None:
                    try:
                        if len(args) >= 3:
                            h_in, s_in, b_in = args[0], args[1], args[2]
                            # Normalize using maxima if provided
                            if maxs is not None and len(maxs) >= 3:
                                h = float(h_in) / float(maxs[0])
                                s = float(s_in) / float(maxs[1])
                                v = float(b_in) / float(maxs[2])
                            else:
                                # Fallback heuristics: if values are <=1 treat
                                # as fractions, otherwise scale assuming common
                                # HSB ranges (h up to 360, s/v up to 255)
                                def _norm_val(x, fallback_div):
                                    xf = float(x)
                                    if xf <= 1.0:
                                        return xf
                                    return xf / float(fallback_div)

                                h = _norm_val(h_in, 360.0)
                                s = _norm_val(s_in, 100.0)
                                v = _norm_val(b_in, 100.0)

                            r, g, b = _hsb_to_rgb_fn(h, s, v)
                            # Handle alpha if present
                            if len(args) >= 4:
                                a_in = args[3]
                                if maxs is not None and len(maxs) >= 4:
                                    af = float(a_in) / float(maxs[3])
                                else:
                                    af = float(a_in)
                                # If caller provided 0..1 floats, keep as fraction
                                if af <= 1.0:
                                    a_val = int(round(af * 255.0))
                                else:
                                    # If supplied in larger-scale (e.g., 0..255), clamp
                                    a_val = int(round(af))
                                return _color_fn(int(r), int(g), int(b), int(a_val))
                            return _color_fn(int(r), int(g), int(b))
                    except Exception:
                        # Fall back to pure _color_fn on any conversion error
                        try:
                            return _color_fn(*args)
                        except Exception:
                            raise
                # Default: delegate to the pure color helper
                return _color_fn(*args)

            engine.api.register('color', lambda *a, **k: _color_wrapper(*a, **k))
            engine.api.register('lerp_color', lambda *a, **k: _lerp_color(*a, **k))

            def _hue(c):
                r, g, b = _unpack_rgb(c)
                h, s, v = _rgb_to_hsb(r, g, b)
                return h

            def _saturation(c):
                r, g, b = _unpack_rgb(c)
                h, s, v = _rgb_to_hsb(r, g, b)
                return s

            def _brightness(c):
                r, g, b = _unpack_rgb(c)
                h, s, v = _rgb_to_hsb(r, g, b)
                return v

            engine.api.register('hue', lambda *a, **k: _hue(a[0] if a else None))
            engine.api.register('saturation', lambda *a, **k: _saturation(a[0] if a else None))
            engine.api.register('brightness', lambda *a, **k: _brightness(a[0] if a else None))
        except Exception:
            # best-effort only; don't fail engine startup if color helpers
            # can't be registered for some reason.
            pass
    except Exception:
        # Best-effort only
        pass


def register_transforms(engine: 'Engine'):
    """Register transform/matrix helpers so they are available via
    the engine API and can be attached to class-based sketch instances.
    """
    try:
        import core.engine.transforms as _t

        engine.api.register('push_matrix', lambda *a, **k: _t.push_matrix(engine, *a, **k))
        engine.api.register('pop_matrix', lambda *a, **k: _t.pop_matrix(engine, *a, **k))
        # short aliases
        engine.api.register('push', lambda *a, **k: _t.push_matrix(engine, *a, **k))
        engine.api.register('pop', lambda *a, **k: _t.pop_matrix(engine, *a, **k))
        engine.api.register('translate', lambda *a, **k: _t.translate(engine, *a, **k))
        engine.api.register('rotate', lambda *a, **k: _t.rotate(engine, *a, **k))
        engine.api.register('scale', lambda *a, **k: _t.scale(engine, *a, **k))
        engine.api.register('shear_x', lambda *a, **k: _t.shear_x(engine, *a, **k))
        engine.api.register('shear_y', lambda *a, **k: _t.shear_y(engine, *a, **k))
        engine.api.register('reset_matrix', lambda *a, **k: _t.reset_matrix(engine, *a, **k))
        engine.api.register('apply_matrix', lambda *a, **k: _t.apply_matrix(engine, *a, **k))
    except Exception:
        # best-effort only
        pass
