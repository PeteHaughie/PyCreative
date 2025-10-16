"""Small helpers to import modules/classes from arbitrary file paths.

These helpers are useful for examples and sketches that live outside a
proper package layout (for example, user-provided examples folders).
They intentionally avoid mutating sys.path and instead use importlib
mechanisms to load modules by absolute path.
"""
from __future__ import annotations

from importlib import util
from types import ModuleType
from pathlib import Path
from typing import Optional, Any
import sys


def load_module_from_path(path: str, module_name: Optional[str] = None) -> ModuleType:
    """Load a module from a filesystem path and return the module object.

    path: absolute or relative path to the .py file
    module_name: optional name to assign to the module (defaults to file stem)
    """
    p = Path(path)
    if module_name is None:
        module_name = p.stem
    spec = util.spec_from_file_location(module_name, str(p))
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot create module spec for {path}')
    mod = util.module_from_spec(spec)
    # Temporarily ensure the module's directory is on sys.path so
    # local sibling imports inside the module (e.g. `import ball_class`)
    # resolve as expected. Restore sys.path afterwards.
    parent = str(p.parent)
    inserted = False
    try:
        if parent not in sys.path:
            sys.path.insert(0, parent)
            inserted = True
        spec.loader.exec_module(mod)
    finally:
        if inserted:
            try:
                sys.path.remove(parent)
            except ValueError:
                pass
    return mod


def load_class_from_path(path: str, class_name: str) -> Any:
    """Load a module from path and return the class object named `class_name`.

    Raises ImportError/AttributeError on failure.
    """
    mod = load_module_from_path(path)
    if not hasattr(mod, class_name):
        raise AttributeError(f"Module {mod.__name__} does not contain {class_name}")
    return getattr(mod, class_name)
