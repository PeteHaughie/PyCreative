import importlib.util
import inspect
import pytest

from pathlib import Path


# Skip this module: examples are documentation/sample code and should not be
# treated as part of the unit test suite by default. If you want to re-enable
# these checks during development, remove or comment out the skip below.
pytest.skip("Skipping examples folder checks in CI/regular test runs", allow_module_level=True)


EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


def load_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    loader = spec.loader
    assert loader is not None
    loader.exec_module(mod)
    return mod


def find_sketch_classes(mod):
    classes = []
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        # Heuristic: class defined in module and not from external package
        if obj.__module__ == mod.__name__:
            classes.append(obj)
    return classes


def test_examples_provide_sketch_lifecycle_methods():
    required_methods = {"setup", "update", "draw", "on_event", "teardown", "size", "frame_rate"}

    # Only consider files that are actual example sketches. Helper modules or
    # compatibility shims (e.g., helpers moved into `examples/_helpers`) should
    # not be treated as example sketches. Historically most examples end with
    # `_example.py`; keep a small allowance for `example_sketch.py`.
    py_files = [p for p in EXAMPLES_DIR.glob("*.py") if p.name.endswith("_example.py") or p.name == "example_sketch.py"]
    assert py_files, "No example files found in examples/"

    failures = []
    for p in py_files:
        mod = load_module_from_path(p)
        sketch_classes = find_sketch_classes(mod)
        if not sketch_classes:
            failures.append(f"{p.name}: no sketch class found")
            continue

        for cls in sketch_classes:
            methods = {name for name, val in inspect.getmembers(cls, inspect.isfunction)}
            missing = [m for m in required_methods if m not in methods]
            # on_event, teardown, update can be optional in examples; require at least setup and draw
            if "setup" not in methods or "draw" not in methods:
                failures.append(f"{p.name}.{cls.__name__}: missing required methods: setup/draw")
            # Record missing optional methods as warnings (fail the test for visibility)
            if missing:
                failures.append(f"{p.name}.{cls.__name__}: missing methods: {missing}")

    assert not failures, "\n".join(failures)
