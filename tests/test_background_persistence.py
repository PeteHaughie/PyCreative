import pygame
from pycreative.app import Sketch


class BGSketch(Sketch):
    def setup(self):
        self.size(64, 48)
        # set a non-black background (red)
        self.background(255, 0, 0)
        self.frames = 0

    def draw(self):
        # do not clear the background here; draw a visible point somewhere else
        # so we can assert the original background remains at (0,0)
        self.stroke(0)  # black stroke so the point is visible
        self.point(10, 10)
        self.frames += 1


def test_background_persists_across_frames():
    s = BGSketch()
    # run setup to initialize sketch state (but avoid creating a display)
    s.setup()

    # Attach an offscreen surface so drawing happens into a regular pygame.Surface
    raw = pygame.Surface((64, 48))
    from pycreative.graphics import OffscreenSurface
    s.surface = OffscreenSurface(raw)
    # If setup recorded a pending background (because no Surface existed),
    # apply it now to the offscreen surface (initialize() normally does this).
    from pycreative.app import _PENDING_UNSET
    if getattr(s, "_pending_background", _PENDING_UNSET) is not _PENDING_UNSET:
        try:
            s.surface.clear(s._pending_background)
            s._pending_background = _PENDING_UNSET
        except Exception:
            pass
    # Run multiple draw frames
    for _ in range(5):
        s.draw()

    # After the frames the offscreen surface should have the background color at (0,0)
    c = raw.get_at((0, 0))[:3]
    assert tuple(c) == (255, 0, 0)

    # The drawn point should have been painted at (10,10) and not overwritten
    p = raw.get_at((10, 10))[:3]
    assert tuple(p) != (255, 0, 0)
