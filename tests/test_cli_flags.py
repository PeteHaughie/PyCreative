import importlib
import sys
from types import SimpleNamespace


def test_cli_parses_max_frames_and_headless(monkeypatch, tmp_path):
    """CLI should parse --max-frames and --headless and call Engine.start with them."""
    # Prepare a fake sketch file to import
    sketch_file = tmp_path / "mysketch.py"
    sketch_file.write_text("""
class Sketch:
    def __init__(self):
        self.started = False
    def setup(self):
        self.started = True
    def draw(self):
        pass
""")

    # Add the tmp_path to sys.path so import works
    monkeypatch.syspath_prepend(str(tmp_path))

    # Create a fake Engine that records start() args
    recorded = {}

    class FakeEngine:
        def __init__(self, max_frames=None, headless=False):
            recorded['init_max_frames'] = max_frames
            recorded['init_headless'] = headless

        def register_api(self, api):
            pass

        def start(self, max_frames=None, headless=False):
            recorded['start_max_frames'] = max_frames
            recorded['start_headless'] = headless

    # Monkeypatch the Engine used by the CLI. The project uses 'src' as the
    # package root for tests, so patch 'src.core.engine'.
    monkeypatch.setitem(sys.modules, 'src.core.engine', SimpleNamespace(Engine=FakeEngine))

    # Import CLI and run main with args (use the src package path used in tests)
    cli = importlib.import_module('src.runner.cli')

    # Simulate running: pycreative mysketch --max-frames 10 --headless
    argv = ['pycreative', str(sketch_file.name), '--max-frames', '10', '--headless']
    monkeypatch.setattr(sys, 'argv', argv)

    # Run
    cli.main()

    # Assert Engine.start received the flags
    assert recorded.get('start_max_frames') == 10
    assert recorded.get('start_headless') is True
