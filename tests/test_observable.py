
from pycreative.observable import Observable


def test_on_method_called_on_assignment():
    calls = []

    class Observer(Observable):
        def __init__(self):
            # set initial value
            self.mass = 1.0

        def on_mass(self, new):
            calls.append((new,))

    o = Observer()
    # assign should call on_mass with new value
    o.mass = 2.5
    assert calls == [(2.5,)]


def test_on_method_receives_old_and_new_when_supported():
    observed = []

    class Observer2(Observable):
        def __init__(self):
            self.value = 10

        def on_value(self, old, new):
            observed.append((old, new))

    o = Observer2()
    o.value = 20
    assert observed == [(10, 20)]


def test_explicit_observe_unobserve():
    seen = []

    class Observer3(Observable):
        pass

    o = Observer3()

    def cb(v):
        seen.append(v)

    o.observe('x', cb)
    o.x = 1
    assert seen == [1]

    o.unobserve('x', cb)
    o.x = 2
    # callback removed, list unchanged
    assert seen == [1]
