from pycreative.app import Sketch
import statistics


def test_random_gaussian_statistics():
    s = Sketch()
    # draw a sample of 10000 values
    samples = [s.random_gaussian() for _ in range(10000)]
    mean = statistics.mean(samples)
    stdev = statistics.pstdev(samples)
    # mean should be close to 0 (within 0.1)
    assert abs(mean) < 0.1
    # stdev should be close to 1 (within 0.1)
    assert abs(stdev - 1.0) < 0.1
