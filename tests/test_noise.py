from pycreative.app import Sketch


def test_noise_range_and_repeatability():
    s = Sketch()
    # default noise values should be in 0..1
    vals = [s.noise(i * 0.1) for i in range(50)]
    assert all(0.0 <= v <= 1.0 for v in vals)

    # reseed and ensure deterministic sequence
    s.noise_seed(12345)
    a = [s.noise(i * 0.1) for i in range(20)]
    s.noise_seed(12345)
    b = [s.noise(i * 0.1) for i in range(20)]
    assert a == b
