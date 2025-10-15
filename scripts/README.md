
Install the repository helper pre-commit hook:

        ./scripts/install_package_hook.sh

What this does
- Writes `.git/hooks/pre-commit` locally (not checked into git).
- The hook runs `python3 tools/check_package_exports.py` which fails
    the commit when a folder under `src/core/` contains Python files but
    lacks an `__init__.py`.

Uninstall / reset

To remove the hook, delete the file:

        rm -f .git/hooks/pre-commit

Troubleshooting

- If the installer fails with permission issues, ensure your working
    tree is writable and that `.git/hooks` exists.
- If you want CI to enforce the same check, add `python3 tools/check_package_exports.py`
    to your CI job or include it in `scripts/run_precommit_hooks.sh`.

