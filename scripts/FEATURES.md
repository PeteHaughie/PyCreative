# Feature scaffolding utility

This folder contains `create_feature.py` — a small helper to scaffold a feature skeleton (spec, plan, tasks placeholder, example, and basic test).

Usage
-----

From the repository root:

```bash
python scripts/create_feature.py sketch-lifecycle "Sketch lifecycle"
```

This will create:
- `specs/sketch-lifecycle/spec.md`
- `specs/sketch-lifecycle/plan.md`
- `specs/sketch-lifecycle/tasks.md`
- `examples/sketch-lifecycle_example.py`
- `tests/test_sketch-lifecycle_feature.py`

Add `--commit` to automatically create a git commit (best-effort).

Notes
-----
- The script intentionally skips existing files to avoid overwriting.
- Use the generated templates as starting points; fill in requirements and tasks before implementation.
