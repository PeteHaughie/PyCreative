<!-- Please describe the change and why it matters. Use the checklist below to help reviewers. -->

## Summary

Describe the change in one or two sentences.

## Related issues

Link to any related issue(s) or PR(s).

## Checklist

- [ ] I added tests covering the new behavior (or gave a clear reason why not).
- [ ] I ran `mypy src/` locally and fixed type issues.
- [ ] I ran `ruff check src/ tests/` and addressed any findings.
- [ ] I ran the test suite locally: `pytest -q`.
- [ ] I updated `docs/` where user-visible behavior changed.
- [ ] If this is a migration from a monolithic module into a package, a compatibility shim that re-exports the public API is included and noted here.

For contribution guidance, see `CONTRIBUTING.md` and `docs/package-style.md`.

Additional notes for reviewers:
- Design decisions:
- Potential follow-ups:
