ADR Index
=========

This directory contains Architectural Decision Records (ADRs) for the project.

Existing ADRs
-------------
- `0001-skia-gpu-first.md` — initial GPU-first Skia decision
- `0002-public-shims-and-package-split.md` — public shims and package split
- `0007-skia-gl-backendtexture-fallback.md` — Skia GL backend-texture reliability and chosen FBO-attach fallback

Note about numbering
--------------------
You may notice that numbers `0003`–`0006` are not present. ADR numbering is a simple convention and not required to be contiguous. Gaps can mean:

- ADRs were never created for those numbers (common when numbering ahead or reserving blocks).
- ADRs were added and later removed or moved to another location.
- ADRs exist in a branch or were archived elsewhere.

If you want to check git history for deleted or moved ADRs, you can run these commands from the repo root:

```bash
# show history for the adr directory
git log -- docs/adr

# show deleted files touched under docs/adr
git log --diff-filter=D --summary -- docs/adr

# search the whole history for files with '0003'..'0006' in their names
git log --all --name-only --pretty=format:%H | grep -E "000[3-6]" -n || true
```

If you want, I can search the git history now and attempt to restore any missing ADRs.
