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

Editor hints / VS Code inlay hints (LOW)
-------------------------------------
- Short: provide a recommended VS Code configuration and small typing/docs improvements so contributors get useful inline hints (parameter names, variable types, return types) via Pylance.
- Why: improves onboardability and reduces friction when editing/using the API; lightweight and non-breaking.
- Acceptance:
	* Add a `.vscode/settings.json` with recommended Pylance/inlay-hints settings (enable `python.analysis.inlayHints.*`).
	* Add `pyrightconfig.json` pointing `src/` so Pylance resolves imports and the package layout consistently.
	* Add a short README note in `docs/` describing how to enable/adjust hints locally.
	* Add a tiny docstring to one or two core APIs (`Sketch.point`, `Surface.clear`) to demonstrate hover/signature help.
