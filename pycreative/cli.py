"""
pycreative.cli: Command line interface for running sketches.
"""
import sys
import importlib.util
import pathlib

def run_sketch(path):
    """
    Run a sketch from a Python file at the given path.
    """
    path = pathlib.Path(path)
    spec = importlib.util.spec_from_file_location("user_sketch", str(path))
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(module)
    # If the sketch file has a main or run function, call it
    if hasattr(module, "main"):
        module.main()
    elif hasattr(module, "run"):
        module.run()
    elif hasattr(module, "Sketch"):
        module.Sketch().run()
    else:
        print(f"No entry point found in {path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: pycreative run path/to/sketch.py")
        sys.exit(1)
    run_sketch(sys.argv[1])
