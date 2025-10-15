# ADR 0009 — Explicit package exports and package-level APIs

Status: Accepted

Context
-------
The repository follows an architecture where public shims (under
`src/pycreative`) expose a stable API while implementation details live
under `src/core/`. During refactors we observed a mix of namespace
packages (no `__init__.py`) and explicit packages with `__init__.py`.
This inconsistency caused discovery issues for contributors and tools
(IDEs, type-checkers), and made short-form imports awkward (e.g.,
`from core.random import random` was not always available).

Decision
--------
1. Prefer explicit packages under `src/core/` — every folder intended to
   expose public or package-level APIs must have an `__init__.py`.
2. Expose public API symbols at the package-level `__all__` in
   `__init__.py` so callers can use short-form imports such as
   `from core.random import random`.
3. Keep implementation details in submodules when helpful, but provide
   package-level re-exports for discoverability and tooling.

Consequences
------------
- Pros:
  - Consistent import paths and better IDE/type-checker support.
  - Easier discovery for contributors and automated agents.
  - Simple, short imports for commonly used functions.

- Cons:
  - Slightly more files to maintain (one `__init__.py` per package).
  - Need to be careful to avoid heavy imports in `__init__.py` to
    preserve import-time performance.

Implementation notes
--------------------
- Add `__init__.py` files to `src/core/` packages that should be explicit.
- Re-export public API symbols in `__init__.py` using `from .module import symbol`.
- Keep `__init__.py` light — avoid importing heavy dependencies. Use
  lazy imports inside functions if necessary.
- Update contributor docs (`.github/copilot-instructions.md` and
  `specs/python-organisation-refactor/design_principles.md`) to record
  this pattern.

Enforcement
-----------
- Add a lightweight check `tools/check_package_exports.py` that flags
  folders under `src/core/` containing Python files but missing `__init__.py`.
- Provide an installer `scripts/install_package_hook.sh` to add a local
  pre-commit hook for contributors to run the check before committing.

References
----------
- `.github/copilot-instructions.md` — guidance for AI agents and
  contributors on package exports.
- `specs/python-organisation-refactor/design_principles.md` — formal
  design guidance for contributors.
