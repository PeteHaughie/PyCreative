"""
PyCreative CLI runner
"""
import sys
import importlib.util
import pathlib
import argparse
import inspect
from pycreative.app import Sketch as BaseSketch

# Ensure project root is in sys.path for editable installs
project_root = pathlib.Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def run_sketch(path, max_frames=None):
    path = pathlib.Path(path)
    if not path.exists():
        print(f"Error: Sketch file '{path}' does not exist.")
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("user_sketch", str(path))
    if spec is None or spec.loader is None:
        print(f"Error: Could not load spec for '{path}'.")
        sys.exit(2)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error executing sketch module: {e}")
        sys.exit(2)
    # If the sketch file has a main or run function, call it
    if hasattr(module, "main"):
        print("[pycreative.cli] Found 'main' entry point.")
        module.main()
        return
    if hasattr(module, "run"):
        print("[pycreative.cli] Found 'run' entry point.")
        module.run()
        return
    # Auto-detect any Sketch subclass and run it (prefer over base Sketch)
    found_subclass = False
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, BaseSketch) and obj is not BaseSketch:
            print(f"[pycreative.cli] Found Sketch subclass: {name}")
            found_subclass = True
            try:
                obj().run(max_frames=max_frames)
                return
            except Exception as e:
                print(f"Error running {name}: {e}")
                sys.exit(2)
    # If no subclass found, fallback to Sketch class if present
    if hasattr(module, "Sketch"):
        print("[pycreative.cli] Found 'Sketch' class entry point (fallback).")
        try:
            module.Sketch().run(max_frames=max_frames)
        except Exception as e:
            print(f"Error running Sketch: {e}")
            sys.exit(2)
        return
    if not found_subclass:
        print(f"[pycreative.cli] No Sketch subclass found in {path}.")
    print(f"No entry point found in {path}. Define a main(), run(), Sketch, or a subclass of Sketch.")

def main():
    parser = argparse.ArgumentParser(description="Run a PyCreative sketch.")
    parser.add_argument("sketch_path", help="Path to sketch file")
    parser.add_argument("--max-frames", type=int, default=None, help="Maximum frames to run")
    args = parser.parse_args()
    run_sketch(args.sketch_path, max_frames=args.max_frames)