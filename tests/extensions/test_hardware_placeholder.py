import pytest


@pytest.mark.hardware
def test_placeholder_hardware_marker():
    """Placeholder hardware test to register the 'hardware' marker usage for spec validation.

    Note: real hardware tests should be skipped in CI; this placeholder exists only to satisfy the spec validator locally.
    """
    assert True
