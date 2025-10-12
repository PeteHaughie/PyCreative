from src.runner.cli import parse_args


def test_parse_use_opengl_flag():
    args = parse_args(['examples/sketch_example.py', '--use-opengl'])
    assert args.use_opengl is True
    args2 = parse_args(['examples/sketch_example.py'])
    assert args2.use_opengl is False
