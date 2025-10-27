import importlib.util
import os
import sys
from core.engine.api.simple import SimpleSketchAPI
from core.engine import impl as engine_impl


def test_programmatic_api_records_shape_ops():
    eng = engine_impl.Engine(sketch_module=None, headless=True)
    api = SimpleSketchAPI(eng)

    # size should update engine dimensions
    api.size(80, 60)
    assert eng.width == 80 and eng.height == 60

    # frame_rate should accept ints and reject non-int
    api.frame_rate(30)
    assert eng.frame_rate == 30

    try:
        api.frame_rate('fast')
        raised = False
    except TypeError:
        raised = True
    assert raised, "frame_rate should raise TypeError for non-int values"

    # drawing ops should record commands on graphics buffer
    api.background(10, 20, 30)
    api.fill(255, 0, 0)
    api.no_stroke()
    api.rect(10, 10, 20, 20)
    api.circle(40, 40, 5)
    ops = [c['op'] for c in eng.graphics.commands]
    assert 'background' in ops
    assert 'rect' in ops
    assert 'circle' in ops


def test_class_based_sketch_and_subobject_can_use_api(tmp_path):
    # Define a minimal sketch module with a Sketch class that creates a subobject
    class Mod:
        class Sketch:
            def setup(self):
                # record size and create a helper object that holds a sketch ref
                self.size(40, 30)
                self.helper = Helper(self)

            def draw(self):
                # helper will call API methods on the sketch reference
                self.helper.do_draw()

    # Helper class that mimics the style of examples/Particle.py where it keeps
    # a reference to the sketch and invokes drawing methods via that reference.
    class Helper:
        def __init__(self, sketch):
            # store reference to sketch (the instance created by Engine)
            self.sketch = sketch

        def do_draw(self):
            # use sketch-level APIs (fill, rect, circle)
            self.sketch.background(0)
            self.sketch.fill(0, 255, 0)
            self.sketch.rect(5, 5, 10, 10)
            self.sketch.circle(20, 15, 4)

    eng = engine_impl.Engine(sketch_module=Mod, headless=True)
    # Engine should have normalized sketch instance
    s = eng.sketch
    # call setup/draw lifecycle
    if hasattr(s, 'setup'):
        s.setup()
    if hasattr(s, 'draw'):
        s.draw()

    # Check that the helper's actions recorded drawing commands
    ops = [c['op'] for c in eng.graphics.commands]
    assert 'background' in ops
    assert 'rect' in ops
    assert 'circle' in ops

    # Now also test using the real Particle class from examples (if available)
    # Load Particle.py from examples path if present
    particle_path = os.path.join(os.getcwd(), 'examples', 'Nature of Code', 'chapter04', 'Example_4_07_Particle_System_With_Repeller', 'Particle.py')
    if os.path.exists(particle_path):
        spec = importlib.util.spec_from_file_location('example_particle', particle_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules['example_particle'] = mod
        try:
            spec.loader.exec_module(mod)
            # create a headless engine and expose SimpleSketchAPI to a fake sketch instance
            eng2 = engine_impl.Engine(sketch_module=None, headless=True)
            # create a sketch facade object similar to SimpleSketchAPI-bound instance
            s2 = SimpleSketchAPI(eng2)
            # instantiate the Particle with the sketch facade
            p = mod.Particle(s2, 10, 10)
            # call run() which should record circle and stroke ops
            p.run()
            ops2 = [c['op'] for c in eng2.graphics.commands]
            assert 'circle' in ops2
        except Exception:
            # If loading example fails, fail the test to surface errors
            raise
    else:
        # If example not available, that's fine; just skip that part
        pass
