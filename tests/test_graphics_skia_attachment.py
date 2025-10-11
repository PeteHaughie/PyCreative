"""Red tests for skia <-> pygame attachment behavior in src.core.graphics."""

import importlib
import sys


def test_attach_skia_function_exists_and_raises_without_skia(monkeypatch):
    gmod = importlib.import_module("src.core.graphics")
    assert hasattr(gmod, "attach_skia_to_pygame"), "attach_skia_to_pygame missing"

    # Provide an adapter that simulates missing skia by raising ImportError
    class MissingAdapter:
        @staticmethod
        def MakeSurface(info):
            raise ImportError("skia is not available")

    try:
        try:
            gmod.attach_skia_to_pygame(None, adapter=MissingAdapter())
            raised = False
        except ImportError:
            raised = True
        assert raised, "Expected attach_skia_to_pygame to raise when skia is not available"
    finally:
        pass


def test_attach_skia_returns_surface_when_skia_present(monkeypatch):
    # Provide a fake skia module with minimal Surface functionality
    class FakeSkiaSurface:
        def __init__(self, w, h):
            self.w = w
            self.h = h

    class FakeSkia:
        @staticmethod
        def MakeSurface(info):
            return FakeSkiaSurface(info.get("width"), info.get("height"))

    # Provide a fake adapter directly
    class FakeAdapter:
        @staticmethod
        def MakeSurface(info):
            return FakeSkiaSurface(info.get("width"), info.get("height"))

    gmod = importlib.import_module("src.core.graphics")
    result = gmod.attach_skia_to_pygame(object(), adapter=FakeAdapter())
    assert result is not None
