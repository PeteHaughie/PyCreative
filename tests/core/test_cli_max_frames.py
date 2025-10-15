import sys
from pathlib import Path


def _write_sketch_file(path: Path, out_path: Path, call_no_loop_in_setup: bool = True, call_no_loop_in_draw: bool = False):
    """Write a temporary sketch file that records draw counts to out_path."""
    setup_no_loop = "self.no_loop()" if call_no_loop_in_setup else ""
    draw_no_loop = "self.no_loop()" if call_no_loop_in_draw else ""
    content = f"""from pathlib import Path
_out = Path('{out_path.as_posix()}')
class Sketch:
    def setup(self):
        {setup_no_loop}
        # initialise count file
        _out.write_text('0')

    def draw(self):
        {draw_no_loop}
        try:
            n = int(_out.read_text())
        except Exception:
            n = 0
        n += 1
        _out.write_text(str(n))
"""
    path.write_text(content)


def test_cli_max_frames_overrides_no_loop(tmp_path, monkeypatch):
    sys.path.insert(0, 'src')
    sketch_file = tmp_path / 'sketch_max_override.py'
    out_file = tmp_path / 'draw_count.txt'
    _write_sketch_file(sketch_file, out_file, call_no_loop_in_setup=True)

    # Run the CLI in headless mode requesting 3 frames
    from pycreative.cli import main
    rc = main([str(sketch_file), '--headless', '--max-frames', '3'])
    assert rc == 0

    assert out_file.exists()
    assert int(out_file.read_text()) == 3


def test_cli_no_flag_respects_no_loop_one_shot(tmp_path):
    sys.path.insert(0, 'src')
    sketch_file = tmp_path / 'sketch_no_flag.py'
    out_file = tmp_path / 'draw_count2.txt'
    _write_sketch_file(sketch_file, out_file, call_no_loop_in_setup=True)

    from pycreative.cli import main
    # No --max-frames, headless run should perform one draw due to no_loop()
    rc = main([str(sketch_file), '--headless'])
    assert rc == 0
    assert out_file.exists()
    assert int(out_file.read_text()) == 1
