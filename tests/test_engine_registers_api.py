def test_engine_registers_api():
    from src.core.engine import Engine

    calls = {}

    class Api:
        def register_api(self, engine):
            calls['called'] = True
            calls['engine'] = engine

    e = Engine()
    e.register_api(Api())
    assert calls.get('called', False) is True
    assert calls.get('engine') is e
