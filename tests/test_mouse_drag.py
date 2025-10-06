import pygame

from pycreative.app import Sketch
from pycreative import input as input_mod


class DummySketch(Sketch):
    def __init__(self):
        super().__init__()
        self.moved = 0
        self.dragged = 0

    def mouse_moved(self):
        self.moved += 1

    def mouse_dragged(self):
        self.dragged += 1


def make_event(evt_type, **kwargs):
    return pygame.event.Event(evt_type, **kwargs)


def test_mouse_move_and_drag_calls(monkeypatch):
    # create sketch and ensure initial state
    s = DummySketch()

    # simulate motion with no button pressed: should call mouse_moved
    evt = make_event(pygame.MOUSEMOTION, pos=(10, 20))
    input_mod.dispatch_event(s, evt)
    assert s.moved == 1 and s.dragged == 0

    # simulate button down
    down = make_event(pygame.MOUSEBUTTONDOWN, pos=(10, 20), button=1)
    input_mod.dispatch_event(s, down)
    # simulate motion while pressed: should call mouse_dragged
    evt2 = make_event(pygame.MOUSEMOTION, pos=(15, 25))
    input_mod.dispatch_event(s, evt2)
    assert s.dragged >= 1

    # simulate button up
    up = make_event(pygame.MOUSEBUTTONUP, pos=(15, 25), button=1)
    input_mod.dispatch_event(s, up)
    # motion after release -> moved
    evt3 = make_event(pygame.MOUSEMOTION, pos=(20, 30))
    input_mod.dispatch_event(s, evt3)
    assert s.moved >= 2
