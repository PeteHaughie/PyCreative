"""Run an example sketch in headless Engine for debugging.

Usage:
    python scripts/run_example_headless.py "examples/Nature of Code/chapter00/Example_0_01_Random_Walk/Example_0_01_Random_Walk.py"
"""
import runpy
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print('Usage: python scripts/run_example_headless.py <path-to-example.py>')
    raise SystemExit(2)

path = Path(sys.argv[1])
ns = runpy.run_path(str(path))

# find Sketch class in namespace
Sketch = ns.get('Sketch')
if Sketch is None:
    print('No Sketch class found in', path)
    raise SystemExit(2)

from core.engine import Engine  # noqa: E402

engine = Engine(sketch_module=ns, headless=True)
engine.run_frames(5)

print('Recorded commands:')
for c in engine.graphics.commands:
    print(c)
