import os
import subprocess
import sys
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent.parent
EXAMPLE = HERE / "examples" / "sketch-lifecycle_example.py"


@pytest.mark.integration
def test_run_loop_headless(tmp_path, monkeypatch):
    """Run the sketch example headless for a few frames using the CLI entry.

    This test uses the SDL dummy video driver so it can run in CI without a display.
    """
    if not EXAMPLE.exists():
        pytest.skip("sketch-lifecycle_example.py not found")

    cmd = [
        sys.executable,
        "-m",
        "pycreative.cli",
        str(EXAMPLE),
        "--max-frames",
        "5",
        "--headless",
    ]
    proc = subprocess.run(cmd, cwd=str(HERE), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Return code 0 is success; warn on non-zero but capture output for debugging
    assert proc.returncode == 0, f"CLI run failed: stdout={proc.stdout.decode()} stderr={proc.stderr.decode()}"
