#!/usr/bin/env python3
"""create_feature.py

Scaffold a new feature for the project with minimal files:
  - specs/<slug>/spec.md
  - specs/<slug>/plan.md
  - specs/<slug>/tasks.md
  - examples/<slug>_example.py
  - tests/test_<slug>_feature.py

Usage:
  python scripts/create_feature.py slug "Feature Title"

Optionally set --commit to auto-create a git commit (requires git and a clean repo).
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


SPEC_TEMPLATE = """# Feature spec: {title}

Feature slug: `{slug}`

Overview
--------

Add a short description of the feature and the user value.

Requirements
------------
- FR-XXX: Describe the primary functional requirement for `{slug}`.

Acceptance criteria
-------------------
- Example under `examples/{slug}_example.py` demonstrates the feature.
- Tests under `tests/test_{slug}_feature.py` cover the basic API surface.

Related docs
------------
- See `docs/api-mapping.md` for mapping guidance when implementing APIs inspired by Processing/openFrameworks.
"""

PLAN_TEMPLATE = """# Plan: {title}

This plan documents the high-level approach for implementing the `{slug}` feature.

Phases
------
1. Research / decisions
2. Data model / contracts
3. Tasks and tests
4. Implementation

Constitution checks
-------------------
Ensure this plan aligns with project constitution and coding conventions.
"""

TASKS_TEMPLATE = """# Tasks for feature `{slug}`

## Phase 1 - Design

1. [ ] Create contracts or data model for `{slug}`. [P]
2. [ ] Add example `examples/{slug}_example.py`. [P]

## Phase 2 - Implementation

3. [ ] Implement minimal API surface and unit tests.
4. [ ] Integration: run example and validate manual behavior.

## Notes

Fill with task details and mark [P] for parallelizable tasks.
"""

EXAMPLE_TEMPLATE = """from pycreative import Sketch


class {class_name}(Sketch):
    def setup(self):
        self.size(400, 300)
        self.set_title("{title}")
        self.frame_rate(60)

    def update(self, dt):
        pass

    def draw(self):
        self.clear((30, 30, 30))


if __name__ == "__main__":
    {class_name}().run()
""".strip()

TEST_TEMPLATE = """import importlib.util
import inspect
from pathlib import Path


def test_example_has_setup_and_draw():
    p = Path(__file__).resolve().parent.parent / "examples" / "{slug}_example.py"
    spec = importlib.util.spec_from_file_location(p.stem, p)
    mod = importlib.util.module_from_spec(spec)
    loader = spec.loader
    assert loader is not None
    loader.exec_module(mod)
    classes = [c for __name__ , c in inspect.getmembers(mod, inspect.isclass) if c.__module__ == mod.__name__]
    assert classes, "No example class found"
    cls = classes[0]
    methods = {{name for name, _ in inspect.getmembers(cls, inspect.isfunction)}}
    assert "setup" in methods and "draw" in methods
"""


def safe_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"Skipping existing file: {path}")
        return
    path.write_text(content, encoding="utf8")
    print(f"Created {path}")


def slug_to_class(slug: str) -> str:
    parts = [p.capitalize() for p in slug.replace("-", "_").split("_")]
    return "".join(parts)


def main(argv: list[str] | None = None):
    p = argparse.ArgumentParser()
    p.add_argument("slug")
    p.add_argument("title", nargs="+", help="Feature title")
    p.add_argument("--commit", action="store_true", help="Create a git commit with the scaffolded files")
    args = p.parse_args(argv)

    slug = args.slug
    title = " ".join(args.title)
    class_name = slug_to_class(slug)

    spec_dir = ROOT / "specs" / slug
    spec_md = spec_dir / "spec.md"
    plan_md = spec_dir / "plan.md"
    tasks_md = spec_dir / "tasks.md"
    example_py = ROOT / "examples" / f"{slug}_example.py"
    test_py = ROOT / "tests" / f"test_{slug}_feature.py"

    safe_write(spec_md, SPEC_TEMPLATE.format(slug=slug, title=title))
    safe_write(plan_md, PLAN_TEMPLATE.format(slug=slug, title=title))
    safe_write(tasks_md, TASKS_TEMPLATE.format(slug=slug))
    safe_write(example_py, EXAMPLE_TEMPLATE.format(class_name=class_name, title=title))
    safe_write(test_py, TEST_TEMPLATE.format(slug=slug))

    if args.commit:
        try:
            subprocess.run(["git", "add", str(spec_dir), str(example_py), str(test_py)], check=True)
            subprocess.run(["git", "commit", "-m", f"chore: scaffold feature {slug}: {title}"], check=True)
            print("Committed scaffold to git")
        except Exception as exc:  # pragma: no cover - best-effort
            print("Git commit failed:", exc)


if __name__ == "__main__":
    main()
