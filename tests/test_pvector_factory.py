from pycreative.app import Sketch


def test_factory_call_and_none_handling():
    s = Sketch()
    f = s.pvector

    # callable factory returns a PVector-like object
    v = f(1, 2)
    assert hasattr(v, "x") and hasattr(v, "y")
    assert v.x == 1.0 and v.y == 2.0

    # None coordinates coerce to 0.0
    v0 = f(None, None)
    assert v0.x == 0.0 and v0.y == 0.0


def test_factory_add_sub_two_arg_and_iterable():
    s = Sketch()
    f = s.pvector

    a = f(1, 2)
    b = f(3, 4)

    # two-arg form
    c = f.add(a, b)
    assert c.x == 4.0 and c.y == 6.0

    # iterable single-arg form
    d = f.add([a, b])
    assert d.x == 4.0 and d.y == 6.0

    e = f.sub(a, b)
    assert e.x == -2.0 and e.y == -2.0

    fiter = f.sub([a, b])
    assert fiter.x == -2.0 and fiter.y == -2.0


def test_factory_add_sub_misuse_raises_helpful_error():
    s = Sketch()
    f = s.pvector
    a = f(1, 1)

    # Calling factory.add with a single PVector is a misuse; should raise TypeError
    try:
        f.add(a)
    except TypeError as exc:
        msg = str(exc)
        assert "mutating addition" in msg or "requires two" in msg
    else:
        raise AssertionError("Expected TypeError for misuse of pvector.add")


def test_instance_add_mutates():
    s = Sketch()
    f = s.pvector
    a = f(0, 0)
    b = f(2, 3)
    a.add(b)
    assert a.x == 2.0 and a.y == 3.0

    # instance sub mutates
    a.sub(b)
    assert a.x == 0.0 and a.y == 0.0
