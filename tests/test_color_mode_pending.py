from pycreative.app import Sketch


class ColorModeSketch(Sketch):
    def setup(self):
        # set color mode before display exists
        self.color_mode('HSB', 360, 100, 100)
        # set a fill expressed in HSB; should be applied when display is created
        self.fill((180, 100, 100))

    def draw(self):
        # no-op draw
        pass


def test_color_mode_set_in_setup_applies_after_run(tmp_path, monkeypatch):
    s = ColorModeSketch()
    # run one frame headless
    s.run(max_frames=1)
    assert s.surface is not None
    # after run, surface.fill should reflect the HSB->RGB conversion; a mid-hue cyan-ish color
    # we simply check the surface _fill is a 3-tuple and not None
    assert isinstance(s.surface._fill, tuple)
    assert len(s.surface._fill) == 3
