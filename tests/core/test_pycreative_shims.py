from pathlib import Path

from core.engine import Engine

import pycreative


def test_shims_delegate_to_engine(tmp_path: Path):
    eng = Engine(sketch_module=None, headless=True)
    pycreative.set_current_engine(eng)

    # size should update engine width/height
    pycreative.size(128, 64)
    assert eng.width == 128 and eng.height == 64

    # background should record a background command
    pycreative.background(10, 20, 30)
    assert any(c.get('op') == 'background' for c in eng.graphics.commands)

    # drawing helpers should record commands via registry
    pycreative.rect(1, 2, 3, 4)
    assert any(c.get('op') == 'rect' for c in eng.graphics.commands)

    # save_frame should record a save_frame op (may not write a file)
    out = str(tmp_path / 'frame.png')
    pycreative.save_frame(out)
    assert any(c.get('op') == 'save_frame' for c in eng.graphics.commands)
