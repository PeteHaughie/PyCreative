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
