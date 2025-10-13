"""Lightweight spec validator for PyCreative (partial implementation).

This script implements some of the checks described in
`specs/python-organisation-refactor/rules.yml`. It's intentionally
conservative so CI can run it without heavy tooling.

Checks implemented:
- Ensure `docs/api/` exists when docs_alignment is enabled.
- Ensure snapshot directory exists when snapshot_policy.enabled is true.
- Ensure tests/ directory exists and has top-level folders (core, api, extensions).
- Validate that pytest markers mentioned in rules.yml are present in tests via a quick scan of `tests/` files for '@pytest.mark.<name>' usages.
- Check that workspace is a clean git state when requested (uses 'git status --porcelain').

This is not a full spec validator. It should be extended to run coverage
and doc/test alignment tools if desired.
"""

from __future__ import annotations

import os
import re
import sys
import yaml
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_RULES = ROOT / 'specs' / 'python-organisation-refactor' / 'rules.yml'


def load_rules(path: Path) -> dict:
    with path.open('r', encoding='utf8') as f:
        return yaml.safe_load(f)


def check_docs_api(rules: dict) -> list[str]:
    errs = []
    docs_ok = (ROOT / 'docs' / 'api').exists()
    if rules.get('docs_alignment', {}).get('enforce_api_doc_consistency', False) and not docs_ok:
        errs.append('docs/api/ missing but docs_alignment is enabled')
    return errs


def check_snapshots(rules: dict) -> list[str]:
    errs = []
    snap_cfg = rules.get('snapshot_policy', {})
    if snap_cfg.get('enabled'):
        snap_dir = ROOT / (snap_cfg.get('directory') or 'tests/__snapshots__')
        if not snap_dir.exists():
            errs.append(f"snapshot directory missing: {snap_dir}")
    return errs


def check_test_layout(rules: dict) -> list[str]:
    errs = []
    tests_dir = ROOT / 'tests'
    if not tests_dir.exists():
        errs.append('tests/ directory missing')
        return errs
    # basic expected subfolders
    for name in ('core', 'api', 'extensions'):
        if not (tests_dir / name).exists():
            errs.append(f'tests/{name} missing')
    return errs


def scan_pytest_markers(rules: dict) -> list[str]:
    errs = []
    pytest_opts = rules.get('pytest_options', {})
    markers = pytest_opts.get('markers', [])
    if not markers:
        return errs
    # markers may be a list of strings or a dict in rules.yml
    if isinstance(markers, dict):
        names = list(markers.keys())
    else:
        names = []
        for m in markers:
            if isinstance(m, dict):
                names.extend(list(m.keys()))
            else:
                # string like 'headless: "desc"' or 'headless'
                try:
                    names.append(str(m).split(':', 1)[0].strip())
                except Exception:
                    names.append(str(m))
    # scan tests for @pytest.mark.<name>
    marker_usage = {n: 0 for n in names}
    for p in (ROOT / 'tests').rglob('*.py'):
        try:
            txt = p.read_text(encoding='utf8')
        except Exception:
            continue
        for n in names:
            if re.search(rf"@pytest\.mark\.{re.escape(n)}\b", txt):
                marker_usage[n] += 1
    for n, c in marker_usage.items():
        if c == 0:
            errs.append(f"pytest marker '{n}' not used in tests (expected at least one usage)")
    return errs


def check_git_clean(rules: dict) -> list[str]:
    errs = []
    ci_cfg = rules.get('ci', {})
    if ci_cfg.get('require_clean_git_state'):
        try:
            out = subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True)
            if out.strip():
                errs.append('git working tree is not clean')
        except Exception as e:
            errs.append(f'git status failed: {e}')
    return errs


def main(argv=None) -> int:
    rules = load_rules(SPEC_RULES)
    checks = []
    checks += check_docs_api(rules.get('testing', {}))
    checks += check_snapshots(rules.get('testing', {}))
    checks += check_test_layout(rules.get('testing', {}))
    checks += scan_pytest_markers(rules.get('testing', {}))
    checks += check_git_clean(rules.get('testing', {}))

    if checks:
        print('Spec validation found issues:')
        for c in checks:
            print(' -', c)
        return 2
    print('Spec validation passed (basic checks)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
