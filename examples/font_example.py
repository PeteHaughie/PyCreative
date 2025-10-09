from pycreative.app import Sketch


class FontExample(Sketch):
    """A comprehensive font example showing system font discovery,
    loading a font (system or bundled), setting active fonts/sizes, and
    rendering text under transforms.
    """

    def setup(self):
        # Create a window and title
        self.size(640, 240)
        self.set_title("Font Example — system fonts, load_font, transforms")

        # 1) Inspect available fonts (bundled first, then system names)
        fonts = self.list_fonts()
        if fonts:
            print("Sample fonts:", ", ".join(str(f) for f in fonts[:30]))

        # 2) Prefer a bundled font named 'opensans-regular' if present in sketch data
        chosen = None
        try:
            names_with_paths = self.list_fonts(include_paths=True)
            for name, path in names_with_paths:
                if name and isinstance(name, str) and name.lower().startswith("opensans") and path:
                    # load relative to the sketch data folder
                    # Use only the filename part so Assets can resolve it relative to sketch data
                    fname = path.split("/")[-1].split("\\")[-1]
                    bundled = self.load_font(fname, size=14)
                    if bundled:
                        self.text_font(bundled)
                        chosen = bundled
                        break
        except Exception:
            pass

        # 3) If no bundled font chosen, ask Assets to load a system font name
        if chosen is None:
            try:
                maybe = self.load_font("courier", size=18)
                if maybe:
                    self.text_font(maybe)
                    chosen = maybe
            except Exception:
                pass

        # 4) Demonstrate loading a bundled TTF from sketch data (uncomment if you add a TTF in examples/data)
        # bundled = self.load_font('OpenSans-Regular.ttf', size=56)
        # if bundled:
        #     self.text_font(bundled)

        # 5) Set a default size for name-based font creation
        self.text_size(60)

        # Set a fill color used by text() when color arg is omitted
        self.fill(20, 30, 120)

    def draw(self):
        # Clear background and draw labels showing transforms
        self.background(0)

        # Draw non-transformed text at top-left
        self.use_font("impact", size=48)
        self.push()
        try:
            self.translate(10, 10)
            self.fill(255, 0, 0, 75)
            self.stroke(0, 255, 0, 100)
            self.stroke_width(2)
            self.text("Top-left (no transform)", 0, 0)
        finally:
            self.pop()

        # Draw rotated + scaled text to demonstrate transform propagation
        self.use_font("courier", size=32)
        self.push()
        try:
            self.fill(0, 0, 255, 100)
            self.stroke(255, 0, 0, 75)
            self.translate(100, 70)
            self.rotate(0.3)
            self.scale(1.25)
            # The text origin here is transformed by translate+rotate+scale
            self.text("Transformed text", 0, 0)
        finally:
            self.pop()


if __name__ == "__main__":
    FontExample().run()
