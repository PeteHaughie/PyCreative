import textwrap
from pathlib import Path

from pycreative.shape import load_svg


def write_svg(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "test.svg"
    p.write_text(textwrap.dedent(content))
    return p


def test_s_shorthand_absolute(tmp_path: Path):
    # Uses absolute S (reflect previous control point)
    svg = """
    <svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'>
      <path d='M 10 10 C 20 20 40 20 50 10 S 80  -10 90 10' fill='none' stroke='black'/>
    </svg>
    """
    p = write_svg(tmp_path, svg)
    shp = load_svg(str(p))
    assert shp is not None
    # should have at least one subpath
    assert len(shp.subpaths) >= 1


def test_s_shorthand_relative(tmp_path: Path):
    # Uses relative s shorthand
    svg = """
    <svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'>
      <path d='M 50 50 c 10 10 30 10 40 0 s 30 -20 40 0' fill='none' stroke='black'/>
    </svg>
    """
    p = write_svg(tmp_path, svg)
    shp = load_svg(str(p))
    assert shp is not None
    assert len(shp.subpaths) >= 1


def test_t_shorthand_quadratic(tmp_path: Path):
    # Quadratic shorthand T/t should reflect previous control point
    svg = """
    <svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'>
      <path d='M 20 20 Q 40 0 60 20 T 100 20' fill='none' stroke='black'/>
    </svg>
    """
    p = write_svg(tmp_path, svg)
    shp = load_svg(str(p))
    assert shp is not None
    assert len(shp.subpaths) >= 1


def test_malformed_path_does_not_hang(tmp_path: Path):
    # Truncated tokens (missing params) should not hang or crash the loader
    svg = """
    <svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'>
      <path d='M 10 10 C 20 20 30' fill='none' stroke='black'/>
    </svg>
    """
    p = write_svg(tmp_path, svg)
    shp = load_svg(str(p))
    # loader should return either a shape or None but not hang; assert completion
    assert shp is None or isinstance(shp.subpaths, list)
