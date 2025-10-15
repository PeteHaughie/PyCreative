"""Simple check to ensure packages under src/core use explicit __init__.py files.

Usage:
    python tools/check_package_exports.py

Exits with non-zero code when a folder under src/core contains Python files
but lacks an __init__.py — indicating a namespace package where an explicit
package is desired.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_CORE = os.path.join(ROOT, 'src', 'core')

bad = []
for dirpath, dirnames, filenames in os.walk(SRC_CORE):
    # Skip hidden directories
    if os.path.basename(dirpath).startswith('.'):
        continue
    py_files = [f for f in filenames if f.endswith('.py')]
    if not py_files:
        continue
    # If __init__.py exists, consider it explicit package
    if '__init__.py' in filenames:
        continue
    # Otherwise flag the folder as missing explicit package
    bad.append(os.path.relpath(dirpath, ROOT))

if bad:
    print('Folders under src/core missing __init__.py:')
    for p in bad:
        print('  -', p)
    sys.exit(2)

print('OK: all src/core packages use explicit __init__.py')
sys.exit(0)
