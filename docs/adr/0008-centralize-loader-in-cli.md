# ADR 0008 — Centralize loader behavior in CLI

Status: Accepted
Date: 2025-10-16

Context
-------
Examples in the repository historically included ad-hoc import plumbing
(like `sys.path` manipulations or inline importlib usage) to allow
sibling modules to be imported when the example was run directly. These
patterns spread inconsistently and cluttered example code with
mechanical boilerplate unrelated to the educational purpose of the
examples.

Decision
--------
Centralize module-by-path loading in the `pycreative` CLI. Provide a
small, documented loader utility `core.util.loader.load_module_from_path`
used by the CLI. Examples and sketches should not contain loader or
`sys.path` plumbing — the runner will ensure sibling imports resolve.

Consequences
------------
- Pros
  - Cleaner example files (no loader or sys.path code). Easier for
    authors and learners to read.
  - Single place to maintain loader semantics and handle edge cases (e.g.,
    spaces in paths, temporary sys.path handling).
  - CLI-driven runs (and CI) behave consistently across examples.

- Cons
  - Requires the CLI or a loader-aware runner to execute examples that
    rely on sibling imports. Loading examples by ad-hoc `python` may
    fail unless the folder is made into a package.

Notes
-----
The loader remains available for tooling and test harnesses, but
examples should avoid referencing it directly. If authors intend to
publish examples as reusable libraries, they should convert directories
into proper packages (add `__init__.py`) and use package-style imports.
