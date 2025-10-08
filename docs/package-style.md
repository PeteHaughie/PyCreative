Package-style module design
==========================

Why prefer package-style over monolithic modules
------------------------------------------------

- Easier to test: small modules with focused responsibilities can have targeted unit tests.
- Easier to reason about: a package maps sub-concepts to submodules (core, loader, utils, math).
- Smaller diffs: refactors that split a monolith into a package are simpler to review when done intentionally.
- Better import hygiene: packages allow clear public APIs via `__init__.py` while keeping internal helpers private.
- Backward compatibility: a small shim (single-file) can re-export package internals for older imports.

Conventions and examples
------------------------

- Place related functionality in `pycreative/<feature>/` packages. For example:
  - `pycreative/shape/core.py`  # PShape class and public surface-drawing entrypoints
  - `pycreative/shape/loader.py`  # SVG/OBJ loading and parsing
  - `pycreative/shape/utils.py`  # transforms, parsing helpers
  - `pycreative/shape/__init__.py`  # public API re-exports (PShape, load_svg)

- Keep private helpers out of the package public API. Use leading underscore names or put them in a `_internal.py` when necessary.

- When migrating a monolithic module:
  1. Create the package and move functionality into well-named submodules.
  2. Add `__init__.py` to re-export the stable public API.
  3. Replace the old monolithic module with a tiny compatibility shim that re-exports from the package.
  4. Run typechecks and tests; add focused tests for the loader/parsers.

Guiding rule
------------

Favor package-style design for features larger than ~200 LOC or that contain more than one responsibility (parsing, math, data model, IO). Use a small shim to preserve compatibility for external imports.

When to keep a single module
----------------------------

Small, single-responsibility modules (under ~200 LOC) that are tightly cohesive may remain as single files. Prefer packages when growth or complexity is expected.

Related resources
-----------------

- docs/README.md — project documentation index
- scripts/FEATURES.md — feature planning notes and rationale
