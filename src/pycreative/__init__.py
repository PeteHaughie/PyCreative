"""Top-level package shim for backwards compatibility.

This package exists to provide the console entrypoint `pycreative.cli:main`.
It delegates to the `runner.cli` module in the `src` layout used during
development.
"""

__all__ = ["cli"]
