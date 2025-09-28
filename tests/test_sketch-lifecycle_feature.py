import importlib.util
import inspect
from pathlib import Path


def test_example_has_setup_and_draw():
    p = Path(__file__).resolve().parent.parent / "examples" / "sketch-lifecycle_example.py"
    spec = importlib.util.spec_from_file_location(p.stem, p)
    mod = importlib.util.module_from_spec(spec)
    loader = spec.loader
    assert loader is not None
    loader.exec_module(mod)
    classes = [c for __name__ , c in inspect.getmembers(mod, inspect.isclass) if c.__module__ == mod.__name__]
    assert classes, "No example class found"
    cls = classes[0]
    methods = {name for name, _ in inspect.getmembers(cls, inspect.isfunction)}
    assert "setup" in methods and "draw" in methods
