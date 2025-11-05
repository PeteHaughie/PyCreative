import types

import pytest

from core.io import replay_to_skia_impl as replay_mod


class FakeMatrix:
    def __init__(self, affine):
        self._affine = affine

    def asAffine(self):
        return self._affine

    def asM33(self):
        return self._affine


class FakeCanvas:
    def __init__(self, matrix):
        self._matrix = matrix
        self.setMatrix_called = False
        # provide minimal methods the replayer may call
        self._saved = 0

    def save(self):
        self._saved += 1

    def restore(self):
        if self._saved:
            self._saved -= 1

    def getTotalMatrix(self):
        return self._matrix

    def setMatrix(self, m):
        # record that setMatrix was invoked
        self.setMatrix_called = True


def test_preserve_non_identity_matrix():
    # Arrange: create a fake canvas whose total matrix is a scale (non-identity)
    mat = FakeMatrix([2.0, 0.0, 0.0, 2.0, 0.0, 0.0])
    canvas = FakeCanvas(mat)

    # Ensure replay_mod has a Matrix factory so the code path that might call
    # skia.Matrix() will not fail. Provide a minimal stand-in.
    dummy_skia = types.SimpleNamespace(Matrix=lambda: 'DUMMY')
    orig_skia = getattr(replay_mod, 'skia', None)
    replay_mod.skia = dummy_skia

    try:
        # Act: call replayer with no commands (we only care about the initial
        # matrix handling which happens before any op processing)
        replay_mod.replay_to_skia_canvas([], canvas)

        # Assert: setMatrix should NOT have been called because the canvas
        # already had a non-identity matrix (presenter scale preserved)
        assert not canvas.setMatrix_called
    finally:
        replay_mod.skia = orig_skia


def test_set_identity_when_matrix_identity():
    # Arrange: create a fake canvas whose matrix is identity
    mat = FakeMatrix([1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
    canvas = FakeCanvas(mat)

    dummy_skia = types.SimpleNamespace(Matrix=lambda: 'DUMMY')
    orig_skia = getattr(replay_mod, 'skia', None)
    replay_mod.skia = dummy_skia

    try:
        # Act
        replay_mod.replay_to_skia_canvas([], canvas)

        # Assert: setMatrix should have been invoked because the replayer
        # sets an explicit identity matrix when the canvas is identity.
        assert canvas.setMatrix_called
    finally:
        replay_mod.skia = orig_skia
