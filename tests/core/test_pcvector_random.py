import pytest
from core.math import PCVector


def test_random2d_exists_and_magnitude():
    if not hasattr(PCVector, 'random2d'):
        pytest.skip('random2d not implemented')
    r = PCVector.random2d()
    assert isinstance(r, PCVector)
    assert pytest.approx(r.mag(), rel=1e-6) == 1.0
    r2 = PCVector.random2d(5)
    assert pytest.approx(r2.mag(), rel=1e-6) == 5.0


def test_random2d_heading_variability():
    if not hasattr(PCVector, 'random2d'):
        pytest.skip('random2d not implemented')
    headings = {round(PCVector.random2d().heading(), 3) for _ in range(30)}
    assert len(headings) > 1
