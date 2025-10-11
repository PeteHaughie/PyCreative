import yaml
import os
import sys

spec = yaml.safe_load(open("specs/python-organisation-refactor/structure.yml"))
rules = yaml.safe_load(open("specs/python-organisation-refactor/rules.yml"))

missing = []
for mod_name, mod in spec["modules"].items():
    for f in mod.get("tests", {}).get("expected_files", []):
        if not os.path.exists(f):
            missing.append(f)

if missing:
    print("❌ Missing test files:")
    for f in missing:
        print(f"  -", f)
    sys.exit(1)

print("✅ Spec test validation passed.")
