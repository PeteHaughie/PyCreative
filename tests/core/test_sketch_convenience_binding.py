from types import SimpleNamespace

from core.engine.impl import Engine


def test_simplesketchapi_exposes_center_constant():
    eng = Engine(headless=True)
    from core.engine.api import SimpleSketchAPI
    api = SimpleSketchAPI(eng)
    assert hasattr(api, 'CENTER')
    assert api.CENTER == 'CENTER'


def test_class_sketch_receives_ellipse_mode_and_center():
    # Create a module-like object with a Sketch class that uses convenience APIs
    class Sketch:
        def __init__(self):
            pass

        def draw(self):
            # Access the Processing-style constant and call ellipse_mode
            # If these bindings are missing this will raise AttributeError
            try:
                self.rect_mode(self.CENTER)
                self.ellipse_mode(self.CENTER)
            except Exception:
                # Re-raise for the test to catch
                raise
            # Record a simple circle so we can assert something was drawn
            self.circle(10, 10, 5)

    mod = SimpleNamespace(Sketch=Sketch)
    eng = Engine(sketch_module=mod, headless=True)
    # Run one frame to invoke draw(); should not raise
    eng.run_frames(1)
    # Ensure the drawing command was recorded
    circles = [c for c in eng.graphics.commands if c.get('op') == 'circle']
    assert len(circles) >= 1
