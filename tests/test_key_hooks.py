def test_key_pressed_hook(monkeypatch):
    # Use dummy video driver so pygame can initialise in CI
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    import pygame
    from types import SimpleNamespace
    from pycreative.input import dispatch_event
    from pycreative.app import Sketch

    pygame.init()
    try:
        class S(Sketch):
            def __init__(self):
                super().__init__()
                self.called = 0

            def key_pressed(self):
                self.called += 1

        s = S()

        # Simulate KEYDOWN for space
        raw_down = SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_SPACE)
        dispatch_event(s, raw_down)
        # dispatch_event updates state and calls key_pressed
        assert s.key_is_pressed is True
        # space name should be set
        assert s.key == 'space'

        # Simulate KEYUP for space
        raw_up = SimpleNamespace(type=pygame.KEYUP, key=pygame.K_SPACE)
        dispatch_event(s, raw_up)
        assert s.key_is_pressed is False
    finally:
        pygame.quit()
