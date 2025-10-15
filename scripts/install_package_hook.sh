#!/usr/bin/env bash
# Install a git pre-commit hook that runs the package-export checker.
set -euo pipefail

HOOK_PATH=".git/hooks/pre-commit"
echo "Installing pre-commit hook to ${HOOK_PATH}"
cat > "${HOOK_PATH}" <<'HOOK'
#!/usr/bin/env bash
# Pre-commit hook: ensure explicit package exports under src/core
python3 tools/check_package_exports.py || {
  echo "Package export check failed. Please add __init__.py to the listed folders." >&2
  exit 1
}
HOOK
chmod +x "${HOOK_PATH}"
echo "Installed pre-commit hook."
