def test_register_api_wires_functions(engine):
    """Confirm that calling register_api with a module/function registers API functions."""

    # define a tiny API module as a simple object with register_api
    class myapi:
        def hello():
            return 'world'

        @staticmethod
        def register_api(engine):
            engine.api.register('hello', myapi.hello)

    # register and verify
    engine.register_api(myapi)
    fn = engine.api.get('hello')
    assert callable(fn)
    assert fn() == 'world'
