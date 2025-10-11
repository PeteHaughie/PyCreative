def test_engine_attaches_skia_on_start(fail_after):
    from src.core.engine import Engine
    from src.core import graphics

    created = {}

    class FakeAdapter:
        @staticmethod
        def MakeSurface(info):
            created['info'] = info
            return {'fake_surface': True, **info}

    # Create engine and call start with an injected adapter via register_api
    e = Engine()

    # Register a fake graphics API that the Engine can call during start.
    class GraphicsAPI:
        def __init__(self, adapter):
            self.adapter = adapter

        def register_api(self, engine):
            # Engine should store or use the adapter when starting
            engine._graphics_adapter = self.adapter

    e.register_api(GraphicsAPI(FakeAdapter()))

    # Start the engine: expected to call attach_skia_to_pygame with adapter
    with fail_after(3):
        e.start()

    # After start, expect engine to have a skia surface stored
    assert getattr(e, '_skia_surface', None) is not None
    assert created.get('info') is not None
