"""Small example for Observable mixin.

Run with:
    pycreative examples/observable_example.py

This example is intentionally minimal: a simple object uses `on_value_change`
handler so assignment updates product automatically.
"""

from pycreative.observable import Observable


class SimpleObserver(Observable):
    def __init__(self):
        self.value = 1.0
        self.product = self.value * 8

    # any method named on_<attr> will be called automatically on assignment to <attr>
    def on_value_change(self, new):
        self.product = float(new) * 8


def main():
    m = SimpleObserver()
    print("initial value", m.value, "product", m.product)
    m.value = 3.5
    print("after set value", m.value, "product", m.product)


if __name__ == "__main__":
    main()
