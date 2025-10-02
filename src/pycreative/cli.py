"""
PyCreative CLI runner
"""

import argparse
import importlib.util
import inspect
import pathlib
import sys
import os

# Avoid importing pycreative.app at module import time to prevent heavy side-effects
# (pygame prints to stdout when imported). We'll import lazily in run_sketch().

# Ensure project root is in sys.path for editable installs
# Determine repository root by searching upward for pyproject.toml so we can
# read project metadata (version) even when running from installed package.
_p = pathlib.Path(__file__).resolve()
project_root = _p
for _ in range(6):
    if (project_root / "pyproject.toml").exists():
        break
    if project_root.parent == project_root:
        break
    project_root = project_root.parent
project_root = project_root if (project_root / "pyproject.toml").exists() else pathlib.Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def run_sketch(path, max_frames=None, debug: bool = False):
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
    # Lazy import BaseSketch to avoid importing pygame when running --help/--version
    try:
        from pycreative.app import Sketch as BaseSketch
    except Exception:
        BaseSketch = None

    found_subclass = False
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and BaseSketch is not None:
            try:
                is_sub = issubclass(obj, BaseSketch)
            except Exception:
                is_sub = False
            if is_sub and obj is not BaseSketch:
                print(f"[pycreative.cli] Found Sketch subclass: {name}")
                found_subclass = True
                try:
                    obj(sketch_path=str(path)).run(max_frames=max_frames, debug=debug)
                    return
                except Exception as e:
                    print(f"Error running {name}: {e}")
                    sys.exit(2)
    # If no subclass found, fallback to Sketch class if present
    if hasattr(module, "Sketch"):
        print("[pycreative.cli] Found 'Sketch' class entry point (fallback).")
        try:
            module.Sketch(sketch_path=str(path)).run(max_frames=max_frames, debug=debug)
        except Exception as e:
            print(f"Error running Sketch: {e}")
            sys.exit(2)
        return
    if not found_subclass:
        print(f"[pycreative.cli] No Sketch subclass found in {path}.")
    print(
        f"No entry point found in {path}. Define a main(), run(), Sketch, or a subclass of Sketch."
    )


def main():
    parser = argparse.ArgumentParser(description="Run a PyCreative sketch.")
    parser.add_argument("sketch_path", nargs="?", help="Path to sketch file")
    parser.add_argument(
        "--max-frames", type=int, default=None, help="Maximum frames to run"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode by setting SDL_VIDEODRIVER=dummy",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug output during sketch startup",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print package version and exit",
    )
    args = parser.parse_args()
    if args.version:
        ver = None
        # First try to get the installed package version (works for installed wheels)
        try:
            try:
                from importlib.metadata import version as _version

                ver = _version("pycreative")
            except Exception:
                # Python <3.8 fallback path is unlikely here; keep broad except
                ver = None
        except Exception:
            ver = None

        # If not installed, fallback to reading pyproject.toml in the repo
        if ver is None:
            pyproject = project_root / "pyproject.toml"
            if pyproject.exists():
                try:
                    try:
                        import tomllib

                        with pyproject.open("rb") as f:
                            data = tomllib.load(f)
                        ver = data.get("project", {}).get("version")
                    except Exception:
                        for line in pyproject.read_text(encoding="utf8").splitlines():
                            s = line.strip()
                            if s.startswith("version") and "=" in s:
                                parts = s.split("=", 1)[1].strip()
                                if parts.startswith('"') and parts.endswith('"'):
                                    ver = parts.strip('"')
                                    break
                except Exception:
                    ver = None

        print(f"pycreative {ver}" if ver else "pycreative (unknown)")
        return
    # Require a sketch path unless --version was passed
    if not args.sketch_path:
        parser.error("sketch_path is required unless --version is used")
    if args.headless:
        # Set dummy driver early so pygame picks it up
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    run_sketch(args.sketch_path, max_frames=args.max_frames, debug=args.debug)


if __name__ == "__main__":
    main()
