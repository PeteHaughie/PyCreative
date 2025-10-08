Contributing to PyCreative
=========================

Thanks for helping improve PyCreative! This file contains the minimal, practical guidance we ask contributors to follow so PRs are easy to review and maintain.

1) Design and layout
--------------------

- Prefer package-style design for features that exceed ~200 lines or that have multiple responsibilities (parsing, math, IO, data model). See `docs/package-style.md` for examples and migration steps.
- Keep public API surface small and stable. Expose public symbols via `__init__.py` in a package; keep helpers private or in `_internal.py`.
- If you're migrating a monolithic module into a package, include a tiny compatibility shim at the original import path that re-exports the new package API. That helps downstream users and CI while the change lands.

2) Tests, type checks, and linting
---------------------------------

- Add unit tests for new functionality and for any non-trivial parser/IO logic (for example, SVG path parsing). Place tests under `tests/` and mark long-running integration tests with `@pytest.mark.integration`.
- Run the full test suite locally before opening a PR: `pytest -q`.
- Run static checks before pushing:

```bash
source .venv/bin/activate
mypy src/
ruff check src/ tests/
pytest -q
```

3) Documentation and examples
----------------------------

- Update `docs/` when adding features or changing public APIs. Add a short example under `examples/` for runtime behavior changes.
- Add a short note in `docs/README.md` to point readers to new docs when appropriate.

4) PR checklist
---------------

- [ ] The change includes tests covering the new behavior (or a clear reason why not).
- [ ] The change passes `mypy` and `ruff` locally.
- [ ] The change updates `docs/` where user-visible behavior changed.
- [ ] Any migration from monolithic modules into new packages includes a compatibility shim and a note in the changelog/PR description.
- [ ] The PR description explains the design, limitations, and the minimal reproduction steps if relevant.

5) Contact and review
---------------------

If you're unsure about the API or package layout, open an issue or draft PR first and request feedback. We're happy to iterate on the design.

Thank you for contributing!
Developer checklist
-------------------

Run the project's CI checks locally before opening a PR:

```bash
./scripts/ci-checks.sh
```

This runs:
- ruff (lint)
- mypy (type-check)
- pytest (tests)

Note: `examples/` and `sketches/` are excluded from linting and type-checks by default because they are experimental sketches and do not follow the project's library typing/style rules.

The GitHub Actions CI runs the same steps in the workflow at `.github/workflows/ci.yml`.

If you prefer manual commands:

```bash
pip install -e '.[test]'
pip install --upgrade ruff mypy
ruff check . --extend-exclude examples --extend-exclude sketches
mypy --config-file pyproject.toml
pytest -q
```

If you'd like to also run editor-style checks (pyright/pylance), install Node and run `pyright`.
