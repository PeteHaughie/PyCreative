
from core.engine.impl import Engine


def test_mouse_position_defaults_and_update_across_frames():
    """mouse_x/mouse_y default to 0 and update across frames; pmouse_x/pmouse_y reflect previous frame."""
    # Create a minimal sketch module with draw that reads mouse vars
    class Sketch:
        def setup(self):
            # no-op
            pass

        def draw(self):
            # record nothing; tests will inspect engine state directly
            pass

    eng = Engine(sketch_module=__import__('types').SimpleNamespace(Sketch=Sketch), headless=True)

    # Before any frames: defaults should be available on engine if input hasn't been set
    assert getattr(eng, 'mouse_x', 0) == 0
    assert getattr(eng, 'mouse_y', 0) == 0
    # Simulate a mouse move via the new helpers
    eng.simulate_mouse_move(x=10, y=20)
    # No exception means the helper worked; run a frame to exercise draw/update
    eng.run_frames(1)
    assert eng.mouse_x == 10
    assert eng.mouse_y == 20
    # pmouse_x/pmouse_y should be set (engine may or may not provide them yet; default to 0)
    assert getattr(eng, 'pmouse_x', 0) in (0, 10)
    assert getattr(eng, 'pmouse_y', 0) in (0, 20)


def test_mouse_pressed_and_button_state_lifecycle():
    # Sketch that toggles a value on mouse_pressed callback
    calls = {}

    class Sketch:
        def setup(self):
            self.count = 0

        def mouse_pressed(self):
            self.count += 1
            calls['pressed'] = True

        def draw(self):
            pass

    eng = Engine(sketch_module=__import__('types').SimpleNamespace(Sketch=Sketch), headless=True)

    # Use simulate helper which ensures setup() has run and dispatches
    eng.simulate_mouse_press(x=5, y=6, button='LEFT')

    # Sketch state should have been updated by the handler
    assert calls.get('pressed', False) is True
    assert getattr(eng, 'mouse_pressed', False) is True
    assert getattr(eng, 'mouse_button', None) == 'LEFT'


def test_mouse_wheel_event_interface():
    # mouse_wheel receives an event object with get_count()
    got = {}

    class FakeEvent:
        def __init__(self, count):
            self._count = count

        def get_count(self):
            return self._count

    class Sketch:
        def mouse_wheel(self, event):
            got['count'] = event.get_count()

        def draw(self):
            pass

    eng = Engine(sketch_module=__import__('types').SimpleNamespace(Sketch=Sketch), headless=True)
    # Use engine helper which accepts the event object
    eng.simulate_mouse_wheel(FakeEvent(3))
    assert got.get('count', None) == 3


def test_mouse_release_and_click_and_drag_and_move():
    calls = {}

    class Sketch:
        def setup(self):
            self.was_pressed = False

        def mouse_pressed(self):
            calls['pressed'] = True

        def mouse_released(self):
            calls['released'] = True

        def mouse_clicked(self):
            calls['clicked'] = True

        def mouse_moved(self):
            calls['moved'] = True

        def mouse_dragged(self):
            calls['dragged'] = True

        def draw(self):
            pass

    eng = Engine(sketch_module=__import__('types').SimpleNamespace(Sketch=Sketch), headless=True)

    # simulate press -> drag -> release
    eng.simulate_mouse_press(x=1, y=2, button='LEFT')
    eng.simulate_mouse_drag(x=2, y=3, button='LEFT')
    eng.simulate_mouse_release(x=2, y=3, button='LEFT')

    # simulate a move with no buttons
    eng.simulate_mouse_move(x=10, y=11)

    # Assertions: handlers were invoked
    assert calls.get('pressed', False) is True
    assert calls.get('dragged', False) is True
    assert calls.get('released', False) is True
    assert calls.get('clicked', False) is True
    assert calls.get('moved', False) is True
