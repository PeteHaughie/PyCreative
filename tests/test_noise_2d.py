def test_noise_2d_accepts_two_args_and_is_deterministic():
    """Ensure the noise() module supports 2D calls and is deterministic when seeded."""
    from pycreative.noise import noise, seed

    # reseed and sample a point
    seed(12345)
    v1 = noise(0.5, 0.25)

    assert isinstance(v1, float)
    assert 0.0 <= v1 <= 1.0

    # reseed and sample again to ensure determinism
    seed(12345)
    v2 = noise(0.5, 0.25)
    assert v1 == v2

    # sanity: sampling a nearby point should usually differ
    v3 = noise(0.5001, 0.25)
    assert isinstance(v3, float)
    assert 0.0 <= v3 <= 1.0
