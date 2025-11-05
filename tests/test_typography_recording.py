import sys
from pathlib import Path


def test_typography_wrapper_and_recording():
    """Engine should attach pycreative typography shims and record text ops

    This test loads the example `examples/typography_demo.py`, instantiates
    an Engine with it, runs a single headless frame, and asserts that:
    - the instantiated sketch has a callable `text` attribute
    - the engine's graphics buffer contains at least one `text` op
    - the recorded `text` op includes a `font_size` value matching the
      size set in the example (48.0)
    """
    # Ensure src is importable
    sys.path.insert(0, str(Path('src').resolve()))

    from core.util.loader import load_module_from_path

    mod = load_module_from_path(str(Path('examples/typography_demo.py').resolve()))

    from core.engine import Engine

    eng = Engine(sketch_module=mod, headless=True)

    # Sketch instance should have a callable `text` method attached
    assert hasattr(eng.sketch, 'text'), 'sketch should have text attribute'
    assert callable(getattr(eng.sketch, 'text')), 'sketch.text should be callable'

    # Run a single frame and inspect recorded commands
    eng.run_frames(1)

    cmds = list(getattr(eng.graphics, 'commands', []))
    text_cmds = [c for c in cmds if c.get('op') == 'text']
    assert text_cmds, f'expected at least one text command, got: {cmds}'

    # Ensure font_size was recorded and matches example's requested size
    found = False
    for c in text_cmds:
        args = c.get('args', {}) or {}
        if 'font_size' in args:
            # Allow small float rounding differences
            assert abs(float(args['font_size']) - 48.0) < 1e-6
            found = True
            break
    assert found, f'no text command contained font_size; text_cmds={text_cmds}'
