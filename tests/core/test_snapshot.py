import os
import tempfile

from core.engine.impl import Engine
from core.engine.snapshot import save_frame


def test_save_frame_hash_expansion(tmp_path):
    eng = Engine(headless=True)
    eng.frame_count = 7
    # relative path with hashes should expand
    out = tmp_path / "outdir"
    out.mkdir()
    filename = "frame-####.png"
    path = os.path.join(str(out), filename)
    save_frame(eng, path)
    expected = os.path.join(str(out), "frame-0007.png")
    assert os.path.exists(expected)


def test_save_frame_default_name(tmp_path):
    eng = Engine(headless=True)
    eng.frame_count = 3
    # empty path should produce screen-0003.png in cwd (we supply cwd)
    cwd = str(tmp_path)
    oldcwd = os.getcwd()
    try:
        os.chdir(cwd)
        save_frame(eng, '')
        assert os.path.exists(os.path.join(cwd, "screen-0003.png"))
    finally:
        os.chdir(oldcwd)
