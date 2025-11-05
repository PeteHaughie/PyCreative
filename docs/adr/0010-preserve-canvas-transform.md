# ADR: Preserve presenter-applied canvas transforms in replayer

Date: 2025-11-05

Context
-------
When replaying recorded drawing commands into a GPU-backed Skia surface the
presenter may apply a logical->backing (device) scale to the Skia canvas to
support HiDPI/Retina displays. Previously the replayer implementation
unconditionally reset the canvas matrix at the start of replay which wiped
out the presenter's scale and caused recorded logical coordinates to be
rendered at the wrong resolution (notably appearing in the upper-left
quadrant when device backing size > logical size).

Decision
--------
Do not unconditionally reset the Skia canvas matrix in the replayer. Instead
inspect the current canvas transform and only set an explicit identity matrix
if the canvas is already identity (or if the matrix cannot be inspected).

Consequences
------------
- Preserves presenter-applied transforms (device-scale) so recorded logical
  drawing commands map to device pixels correctly on HiDPI displays.
- Avoids the half-size quadrant artifact observed when the presenter scaled
  the canvas but the replayer immediately cleared that transform.
- Slightly more defensive codepath in the replayer: we attempt to inspect the
  canvas matrix via available accessors and fall back to no-op on inspection
  failure.

Alternatives considered
-----------------------
- Keep the unconditional reset and change the presenter to pre-scale recorded
  drawing commands to device-pixels before calling the replayer. This couples
  the presenter and replayer responsibilities and increases transformation
  duplication risk.
- Add a flag to the replayer to opt-out of clearing the matrix — this is
  functionally similar to the chosen approach but requires configuration and
  explicit coordination between components.

Status
------
Accepted and implemented. Unit tests added to assert the replayer preserves
non-identity transforms and only resets identity matrices.
