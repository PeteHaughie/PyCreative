class Sketch:
    """Minimal typography demo sketch.

    - sets a readable text size
    - draws a short string
    - queries the public text measurement helpers and draws guide lines

    This sketch is intentionally small so it works with headless or
    fallback environments where a rendering backend may not supply full
    font metrics.
    """

    def setup(self):
        self.size(640, 240)
        self.window_title('Typography demo')
        # Light background and black fill for text
        try:
            self.background(240)
        except Exception:
            pass
        try:
            self.fill(0)
        except Exception:
            pass
        # Pick a comfortable on-canvas font size
        try:
            self.text_size(48)
        except Exception:
            pass

    def draw(self):
        s = 'Hello, PyCreative!'
        x = 40.0
        y = 120.0

        # print(f"Drawing text sample: '{s}' at ({x}, {y})")

        # Use local references so we don't accidentally shadow the sketch API
        text_fn = getattr(self, 'text', None)
        text_width_fn = getattr(self, 'text_width', None)
        text_ascent_fn = getattr(self, 'text_ascent', None)
        text_descent_fn = getattr(self, 'text_descent', None)

        # Draw the text if available
        if callable(text_fn):
            text_fn(s, x, y)

        # Query measurements (fall back to None when not provided)
        w = float(text_width_fn(s)) if callable(text_width_fn) else None
        a = float(text_ascent_fn()) if callable(text_ascent_fn) else None
        d = float(text_descent_fn()) if callable(text_descent_fn) else None

        # Draw guide lines for baseline, ascent and descent when available
        try:
            if w is not None:
                # Baseline (red)
                try:
                    self.stroke(220, 40, 40)
                except Exception:
                    pass
                try:
                    self.line(x, y, x + w, y)
                except Exception:
                    pass

            if a is not None:
                try:
                    self.stroke(40, 180, 40)
                    self.line(x, y - a, x + (w or 120), y - a)
                except Exception:
                    pass

            if d is not None:
                try:
                    self.stroke(40, 40, 220)
                    self.line(x, y + d, x + (w or 120), y + d)
                except Exception:
                    pass

            # Show numeric metrics underneath the sample text
            try:
                self.fill(0)
                info = f"w={w:.1f} a={a:.1f} d={d:.1f}" if (w is not None and a is not None and d is not None) else "metrics N/A"
                if callable(text_fn):
                    text_fn(info, x, y + 60)
            except Exception:
                pass
        except Exception:
            # non-fatal; examples should never crash the runner
            pass
