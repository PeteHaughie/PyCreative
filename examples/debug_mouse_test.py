"""Small interactive sketch to exercise mouse handlers and properties.

Run with:

PYCREATIVE_DEBUG_HANDLER_EXCEPTIONS=1 pycreative examples/debug_mouse_test.py --verbose

"""

class Sketch:
    def setup(self):
        self.size(400, 300)
        self.window_title('Debug Mouse Test')
        print('setup: running')

    def draw(self):
        # show current engine-backed mouse properties
        try:
            mx = self.mouse_x
            my = self.mouse_y
            pmx = self.pmouse_x
            pmy = self.pmouse_y
            btn = self.mouse_button
            pressed = bool(self.mouse_pressed)
        except Exception as e:
            print('draw: property access error', e)
            mx = my = pmx = pmy = btn = pressed = None
        print(f'draw: mouse=({mx},{my}) pmouse=({pmx},{pmy}) btn={btn} pressed={pressed}')

    def mouse_pressed(self):
        print('handler: mouse_pressed called; engine pressed=', bool(self.mouse_pressed), 'button=', self.mouse_button)

    def mouse_released(self):
        print('handler: mouse_released called; engine pressed=', bool(self.mouse_pressed), 'button=', self.mouse_button)

    def mouse_moved(self):
        print('handler: mouse_moved called; mouse=', self.mouse_x, self.mouse_y)

    def mouse_dragged(self):
        print('handler: mouse_dragged called; mouse=', self.mouse_x, self.mouse_y)

    def mouse_wheel(self, event):
        try:
            print('handler: mouse_wheel called; count=', event.get_count())
        except Exception:
            print('handler: mouse_wheel called; bad event')
