import pygame

from pycreative.app import Sketch


class DrawOnceSketch(Sketch):
    def setup(self):
        self.size(80, 60)
        self.draw_count = 0

    def update(self, dt):
        pass

    def draw(self):
        # increment draw counter and request no_loop to stop further draws
        self.draw_count += 1
        if self.draw_count == 1:
            self.no_loop()


def test_no_loop_called_inside_draw_runs_only_once():
    pygame.init()
    s = DrawOnceSketch()
    s.setup()
    # run the sketch for a few frames; no_loop should stop drawing after one
    s.run(max_frames=5)
    assert s.draw_count == 1
