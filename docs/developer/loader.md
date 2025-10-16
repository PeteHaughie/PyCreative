# Loader utility (developer docs)

This project includes a small helper utility to load Python modules and
classes directly from filesystem paths. It is intended for examples and
sketches that aren't laid out as importable packages (for example, a
user-created example folder containing several related .py files).

Why we have this
- Many examples are distributed as plain .py files that import sibling
  modules using simple `import sibling` statements. Running those files
  directly (or using `runpy.run_path`) will fail unless the example
  directory is on `sys.path`.
- The loader provides an explicit, minimal API to load files by path
  while ensuring those local sibling imports resolve during module
  execution.

Location
- `src/core/util/loader.py`

API
- `load_module_from_path(path: str, module_name: Optional[str] = None) -> ModuleType`
  - Loads the module at `path` and returns the loaded module object.
  - Temporarily inserts the module's parent directory at the front of
    `sys.path` while executing the module so relative sibling imports
    succeed. The path is removed afterwards.
  - `module_name` controls the assigned module name (defaults to file stem).

- `load_class_from_path(path: str, class_name: str) -> Any`
  - Convenience wrapper; returns the named class object from the module
    loaded from `path`.

Usage examples

1) Load a sketch module and pass it to the Engine (recommended when
   running an example file directly):

```py
from core.util.loader import load_module_from_path
from core.engine import Engine
mod = load_module_from_path('examples/Bouncing Balls/bouncing_balls_class_example.py')
eng = Engine(sketch_module=mod, headless=True)
eng.run_frames(1)
```

2) Load just a class from a file:

```py
from core.util.loader import load_class_from_path
Ball = load_class_from_path('examples/Bouncing Balls/ball_class.py', 'Ball')
ball = Ball()
```

Recommendations
- Prefer converting long-lived example folders into proper packages
  (add `__init__.py` and use package imports) if you intend to reuse the
  code widely. The loader is ideal for ad-hoc examples and user
  sketches, not as a replacement for good packaging.
- Avoid permanently mutating `sys.path` in scripts; use the loader where
  possible to keep import side-effects localized.

Notes
- The loader is intentionally small and dependency-free.
- It does not sandbox loaded modules — imported code runs with the
  usual Python semantics and may have side effects.

CLI integration
----------------

The preferred way to run examples that import sibling modules is via the
`pycreative` CLI. The CLI uses `core.util.loader.load_module_from_path`
to load sketch files and ensures the module's parent directory is
available during execution so local imports work. This keeps example
files free of loader plumbing and provides a consistent entrypoint for
running sketches in CI and development.

When authoring examples, assume the runner will handle loader semantics
and avoid adding `sys.path` mutations or loader calls inside sketch
files. See `pycreative/cli.py` for the integration details.

